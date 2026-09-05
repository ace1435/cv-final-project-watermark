import cv2
import numpy as np
import pywt
from imwatermark.dwtDctSvd import EmbedDwtDctSvd

from wmbench.watermarkers.common import base


class scored_dwtdctsvd(EmbedDwtDctSvd):
    def decode_scores(self, bgr):
        row, col, _ = bgr.shape
        yuv = cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV)
        scores = [[] for i in range(self._wmLen)]
        for channel in range(2):
            if self._scales[channel] <= 0:
                continue
            ca1, _ = pywt.dwt2(yuv[: row // 4 * 4, : col // 4 * 4, channel], "haar")
            scores = self.decode_frame(ca1, self._scales[channel], scores)
        return np.array([np.mean(s) for s in scores])


class dwtdct(base):
    name = "dwtdct"
    nbits = 32
    native_strength = 36.0

    def make(self, bits, strength):
        return scored_dwtdctsvd(watermarks=[int(b) for b in bits], wmLen=self.nbits, scales=[0, strength, 0], block=4)

    def embed(self, img, bits, strength):
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        marked = self.make(bits, strength).encode(bgr)
        return cv2.cvtColor(marked, cv2.COLOR_BGR2RGB)

    def decode(self, img, strength=None):
        scale = self.native_strength if strength is None else strength
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        votes = self.make([0] * self.nbits, scale).decode_scores(bgr)
        return 2.0 * votes - 1.0
