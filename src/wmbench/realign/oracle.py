import cv2
import numpy as np


def realign(transformed, matrix, shape, valid=None, cover=None):
    h, w = shape[:2]
    m = np.asarray(matrix, dtype=np.float64)[:2]
    flags = cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP
    back = cv2.warpAffine(transformed, m, (w, h), flags=flags, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    ones = np.full(transformed.shape[:2], 255, np.uint8)
    covered = cv2.warpAffine(ones, m, (w, h), flags=cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_CONSTANT, borderValue=0) > 0
    mask = covered if valid is None else covered & valid
    if cover is not None:
        back = np.where(mask[:, :, None], back, cover)
    else:
        back = np.where(mask[:, :, None], back, 0).astype(np.uint8)
    return back, mask
