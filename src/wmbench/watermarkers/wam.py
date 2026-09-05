import json
import sys

import numpy as np
import omegaconf
import torch

from wmbench.watermarkers.common import base, bits_to_tensor, models_root, normalize, pick_device, root, to_tensor, to_uint8, unnormalize

repo = root / "third_party" / "watermark_anything"
if str(repo) not in sys.path:
    sys.path.insert(0, str(repo))

from watermark_anything.models import Wam, build_embedder, build_extractor
from watermark_anything.modules.jnd import JND


def load_wam(device):
    params = json.loads((repo / "checkpoints" / "params.json").read_text(encoding="utf-8"))
    embedder_cfg = omegaconf.OmegaConf.load(repo / params["embedder_config"])
    extractor_cfg = omegaconf.OmegaConf.load(repo / params["extractor_config"])
    attenuation_cfg = omegaconf.OmegaConf.load(repo / params["attenuation_config"])
    embedder = build_embedder(params["embedder_model"], embedder_cfg[params["embedder_model"]], params["nbits"])
    extractor = build_extractor(extractor_cfg.model, extractor_cfg[params["extractor_model"]], params["img_size"], params["nbits"])
    attenuation = JND(**attenuation_cfg[params["attenuation"]], preprocess=unnormalize, postprocess=normalize)
    model = Wam(embedder, extractor, None, attenuation, params["scaling_w"], params["scaling_i"])
    state = torch.load(models_root() / "wam" / "checkpoint.pth", map_location="cpu", weights_only=True)
    model.load_state_dict(state)
    return model.to(device).eval()


class wam(base):
    name = "wam"
    nbits = 32
    native_strength = 2.0

    def __init__(self):
        self.device = pick_device()
        self.model = load_wam(self.device)

    def embed(self, img, bits, strength):
        self.model.scaling_w = strength
        x = normalize(to_tensor(img, self.device))
        with torch.no_grad():
            out = self.model.embed(x, bits_to_tensor(bits, self.device))
        return to_uint8(unnormalize(out["imgs_w"]))

    def detect_maps(self, img):
        x = normalize(to_tensor(img, self.device))
        with torch.no_grad():
            preds = self.model.detect(x)["preds"]
        return preds[0, 0], preds[0, 1:]

    def decode(self, img, strength=None):
        mask, bits = self.detect_maps(img)
        weight = torch.sigmoid(mask)
        soft = (bits * weight).sum(dim=(1, 2)) / weight.sum().clamp_min(1e-6)
        return soft.float().cpu().numpy()

    def pixel_score(self, img):
        mask, _ = self.detect_maps(img)
        return float((torch.sigmoid(mask) > 0.5).float().mean())
