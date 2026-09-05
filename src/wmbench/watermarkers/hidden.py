import torch

from wmbench.watermarkers.common import base, bits_to_tensor, models_root, normalize, pick_device, to_tensor, to_uint8, unnormalize


class hidden(base):
    name = "hidden"
    nbits = 48
    native_strength = 1.0

    def __init__(self):
        self.device = pick_device()
        folder = models_root() / "hidden"
        self.encoder = torch.jit.load(str(folder / "encoder_with_jnd_48b.torchscript.pt"), map_location=self.device).eval()
        self.decoder = torch.jit.load(str(folder / "decoder_48b.torchscript.pt"), map_location=self.device).eval()

    def embed(self, img, bits, strength):
        x = normalize(to_tensor(img, self.device))
        msg = 2 * bits_to_tensor(bits, self.device) - 1
        with torch.no_grad():
            marked = self.encoder(x, msg)
        delta = marked - x
        return to_uint8(unnormalize(x + strength * delta))

    def decode(self, img, strength=None):
        x = normalize(to_tensor(img, self.device))
        with torch.no_grad():
            logits = self.decoder(x)
        return logits.reshape(-1).float().cpu().numpy()
