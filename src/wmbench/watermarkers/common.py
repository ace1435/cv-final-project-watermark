from pathlib import Path

import numpy as np
import torch
import yaml

root = Path(__file__).resolve().parents[3]
mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)


def pick_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def models_root():
    data = Path(yaml.safe_load((root / "configs" / "remote.yaml").read_text(encoding="utf-8"))["data"])
    if data.exists():
        return data / "models"
    return root / "data" / "images" / "models"


def to_tensor(img, device):
    x = torch.from_numpy(np.array(img, dtype=np.uint8)).permute(2, 0, 1).float() / 255.0
    return x.unsqueeze(0).to(device)


def to_uint8(x):
    x = x.detach().clamp(0, 1).mul(255).round().squeeze(0).permute(1, 2, 0)
    return x.cpu().numpy().astype(np.uint8)


def normalize(x):
    return (x - mean.to(x.device)) / std.to(x.device)


def unnormalize(x):
    return x * std.to(x.device) + mean.to(x.device)


def bits_to_tensor(bits, device):
    return torch.from_numpy(np.asarray(bits)).float().view(1, -1).to(device)


class base:
    name = ""
    nbits = 0
    native_strength = 1.0

    def embed(self, img, bits, strength):
        raise NotImplementedError

    def decode(self, img, strength=None):
        raise NotImplementedError

    def residual(self, img, bits, strength=None):
        strength = self.native_strength if strength is None else strength
        marked = self.embed(img, bits, strength)
        return marked.astype(np.float32) - img.astype(np.float32)

    def random_bits(self, rng):
        return rng.integers(0, 2, self.nbits)
