import cv2
import kornia.feature as kf
import numpy as np
import torch

from wmbench.watermarkers.common import pick_device

match_side = 1024
min_inliers = 15
min_response = 0.3
max_keypoints = 2048

_models = None


def models():
    global _models
    if _models is None:
        device = pick_device()
        disk = kf.DISK.from_pretrained("depth").to(device).eval()
        glue = kf.LightGlue("disk").to(device).eval()
        _models = (disk, glue, device)
    return _models


def gray(img):
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def shrink(img):
    s = min(1.0, match_side / max(img.shape[:2]))
    if s < 1.0:
        img = cv2.resize(img, (round(img.shape[1] * s), round(img.shape[0] * s)), interpolation=cv2.INTER_AREA)
    return img, s


def to_batch(img, device):
    x = torch.from_numpy(np.array(img)).permute(2, 0, 1).float() / 255.0
    return x.unsqueeze(0).to(device)


def features(img):
    disk, glue, device = models()
    with torch.no_grad():
        out = disk(to_batch(img, device), n=max_keypoints, pad_if_not_divisible=True)[0]
    return out.keypoints, out.descriptors


def glue_matches(cover, out):
    disk, glue, device = models()
    k0, d0 = features(cover)
    k1, d1 = features(out)
    if len(k0) < min_inliers or len(k1) < min_inliers:
        return np.zeros((0, 2)), np.zeros((0, 2))
    data = {
        "image0": {"keypoints": k0[None], "descriptors": d0[None], "image_size": torch.tensor([[cover.shape[1], cover.shape[0]]], device=device).float()},
        "image1": {"keypoints": k1[None], "descriptors": d1[None], "image_size": torch.tensor([[out.shape[1], out.shape[0]]], device=device).float()},
    }
    with torch.no_grad():
        result = glue(data)
    pairs = result["matches"][0].cpu().numpy()
    if len(pairs) == 0:
        return np.zeros((0, 2)), np.zeros((0, 2))
    return k0[pairs[:, 0]].cpu().numpy(), k1[pairs[:, 1]].cpu().numpy()


def similarity(src, dst):
    if len(src) < min_inliers:
        return None, 0
    m, inliers = cv2.estimateAffinePartial2D(src.astype(np.float32), dst.astype(np.float32), method=cv2.RANSAC, ransacReprojThreshold=3.0, maxIters=5000, confidence=0.999)
    if m is None or inliers is None:
        return None, 0
    count = int(inliers.sum())
    if count < min_inliers:
        return None, count
    return np.vstack([m, [0, 0, 1]]), count


def phase_shift(cover, out):
    h, w = cover.shape[:2]
    if out.shape[0] > h or out.shape[1] > w:
        return None, 0.0
    canvas = np.zeros((h, w), np.float32)
    canvas[: out.shape[0], : out.shape[1]] = gray(out).astype(np.float32)
    reference = gray(cover).astype(np.float32)
    window = cv2.createHanningWindow((w, h), cv2.CV_32F)
    (dx, dy), response = cv2.phaseCorrelate(reference, canvas, window)
    matrix = np.array([[1.0, 0.0, dx], [0.0, 1.0, dy], [0.0, 0.0, 1.0]])
    return matrix, float(response)


ecc_side = 512


def scale_matrix(f):
    return np.array([[f, 0.0, 0.0], [0.0, f, 0.0], [0.0, 0.0, 1.0]])


def refine_ecc(cover, out, matrix):
    f = min(1.0, ecc_side / max(cover.shape[:2]))
    small_cover = cv2.resize(cover, None, fx=f, fy=f, interpolation=cv2.INTER_AREA) if f < 1 else cover
    small_out = cv2.resize(out, None, fx=f, fy=f, interpolation=cv2.INTER_AREA) if f < 1 else out
    template = gray(small_cover).astype(np.float32) / 255.0
    moving = gray(small_out).astype(np.float32) / 255.0
    reduced = scale_matrix(f) @ matrix @ scale_matrix(1 / f)
    warp = reduced[:2].astype(np.float32).copy()
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 1e-4)
    try:
        cc, refined = cv2.findTransformECC(template, moving, warp, cv2.MOTION_AFFINE, criteria, None, 5)
    except cv2.error:
        return matrix, False
    if not np.all(np.isfinite(refined)) or np.abs(refined - warp).max() > 10 * f:
        return matrix, False
    full = scale_matrix(1 / f) @ np.vstack([refined, [0, 0, 1]]) @ scale_matrix(f)
    return full, True


def estimate(cover, out):
    small_cover, sc = shrink(cover)
    small_out, so = shrink(out)
    src, dst = glue_matches(small_cover, small_out)
    matrix, inliers = similarity(src / sc, dst / so)
    method = "lightglue"
    response = 0.0
    if matrix is None:
        matrix, response = phase_shift(cover, out)
        method = "phase"
        if matrix is None or response < min_response:
            matrix = np.eye(3)
            method = "failed"
    refined = False
    if method != "failed":
        matrix, refined = refine_ecc(cover, out, matrix)
    return matrix, {"method": method, "inliers": inliers, "response": response, "ecc": refined}


def corner_error(estimated, oracle, shape):
    h, w = shape[:2]
    corners = np.array([[0, 0, 1], [w - 1, 0, 1], [0, h - 1, 1], [w - 1, h - 1, 1]], dtype=np.float64).T
    a = (np.asarray(estimated) @ corners)[:2]
    b = (np.asarray(oracle) @ corners)[:2]
    return float(np.linalg.norm(a - b, axis=0).mean())
