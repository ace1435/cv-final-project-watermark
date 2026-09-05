import lpips
import numpy as np
import piq
import torch

from wmbench.watermarkers.common import pick_device, to_tensor


def psnr(a, b):
    mse = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
    if mse == 0:
        return 99.0
    return float(10 * np.log10(255.0 ** 2 / mse))


class scorer:
    def __init__(self):
        self.device = pick_device()
        self.lpips = lpips.LPIPS(net="alex", verbose=False).to(self.device).eval()
        self.dists = piq.DISTS().to(self.device).eval()

    def all(self, a, b):
        x = to_tensor(a, self.device)
        y = to_tensor(b, self.device)
        with torch.no_grad():
            ssim = float(piq.ssim(x, y, data_range=1.0))
            lp = float(self.lpips(x * 2 - 1, y * 2 - 1))
            di = float(self.dists(x, y))
        return {"psnr": psnr(a, b), "ssim": ssim, "lpips": lp, "dists": di}
