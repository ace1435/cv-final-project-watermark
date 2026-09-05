import numpy as np
import torch
from PIL import Image
from torchvision import transforms
from trustmark import TrustMark

from wmbench.watermarkers.common import base, pick_device


class trustmark_q(base):
    name = "trustmark_q"
    nbits = 100
    native_strength = 1.0
    payload_bits = 61

    def __init__(self):
        self.device = pick_device()
        self.tm = TrustMark(use_ECC=False, verbose=False, secret_len=self.nbits, device=str(self.device), model_type="Q", loadRemover=False)

    def embed(self, img, bits, strength):
        text = "".join(str(int(b)) for b in bits)
        out = self.tm.encode(Image.fromarray(img), text, MODE="binary", WM_STRENGTH=strength)
        return np.asarray(out, dtype=np.uint8)

    def decode(self, img, strength=None):
        pil = self.tm.get_the_image_for_processing(Image.fromarray(img))
        pil = pil.resize((self.tm.model_resolution_dec, self.tm.model_resolution_dec), Image.BILINEAR)
        x = transforms.ToTensor()(pil).unsqueeze(0).to(self.tm.decoder.device) * 2.0 - 1.0
        with torch.no_grad():
            logits = self.tm.decoder.decoder(x)
        return logits[0].float().cpu().numpy()

    def random_bits(self, rng):
        payload = "".join(str(int(b)) for b in rng.integers(0, 2, self.payload_bits))
        return self.tm.ecc.encode_binary([payload])[0].astype(np.int64)

    def ecc_ok(self, scores, bits):
        hard = (np.asarray(scores) > 0).astype(np.int64)
        secret, detected, version = self.tm.ecc.decode_bitstream(hard[None, :], "binary")[0]
        payload, _, _ = self.tm.ecc.decode_bitstream(np.asarray(bits)[None, :], "binary")[0]
        return bool(detected) and secret == payload
