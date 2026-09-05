from pathlib import Path

import torch
import videoseal
from omegaconf import OmegaConf
from videoseal.models import Videoseal, build_embedder, build_extractor
from videoseal.modules.jnd import JND
from videoseal.utils.cfg import get_dummy_augmenter

from wmbench.watermarkers.common import base, bits_to_tensor, models_root, pick_device, to_tensor, to_uint8


def load_card(card_name, checkpoint):
    card = OmegaConf.load(Path(videoseal.__file__).parent / "cards" / f"{card_name}.yaml")
    args = card.args
    embedder = build_embedder(card.embedder.model, card.embedder.params, args.nbits, args.get("hidden_size_multiplier", 2))
    extractor = build_extractor(card.extractor.model, card.extractor.params, args.img_size_proc, args.nbits)
    attenuation = JND(in_channels=1, out_channels=1)
    chunk = args.get("videoseal_chunk_size", args.get("videowam_chunk_size"))
    step = args.get("videoseal_step_size", args.get("videowam_step_size"))
    model = Videoseal(embedder, extractor, get_dummy_augmenter(), attenuation=attenuation, scaling_w=args.scaling_w, scaling_i=args.scaling_i, img_size=args.img_size_proc, chunk_size=chunk, step_size=step)
    state = torch.load(checkpoint, map_location="cpu", weights_only=True)
    model.load_state_dict(state["model"], strict=False)
    return model


class pixelseal(base):
    name = "pixelseal"
    nbits = 256
    native_strength = 0.2
    card = "pixelseal"
    checkpoint = "pixelseal.pth"

    def __init__(self):
        self.device = pick_device()
        self.model = load_card(self.card, models_root() / "videoseal" / self.checkpoint).to(self.device).eval()

    def embed(self, img, bits, strength):
        self.model.blender.scaling_w = strength
        x = to_tensor(img, self.device)
        with torch.no_grad():
            out = self.model.embed(x, bits_to_tensor(bits, self.device), is_video=False)
        return to_uint8(out["imgs_w"])

    def detect(self, img):
        x = to_tensor(img, self.device)
        with torch.no_grad():
            preds = self.model.detect(x, is_video=False)["preds"]
        return preds[0].float().cpu().numpy()

    def decode(self, img):
        return self.detect(img)[1:]

    def detect_logit(self, img):
        return float(self.detect(img)[0])


class videoseal_1(pixelseal):
    name = "videoseal_1"
    card = "videoseal_1.0"
    checkpoint = "y_256b_img.pth"
