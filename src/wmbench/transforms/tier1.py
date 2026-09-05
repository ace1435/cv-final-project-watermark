import io
import math
from pathlib import Path

import cv2
import numpy as np
import yaml
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[3]
config = yaml.safe_load((root / "configs" / "transforms.yaml").read_text(encoding="utf-8"))
families = config["families"]
kernels = {"bilinear": cv2.INTER_LINEAR, "area": cv2.INTER_AREA, "bicubic": cv2.INTER_CUBIC, "lanczos": cv2.INTER_LANCZOS4}
caption_text = "shared from my phone, look at this"


def conditions(smoke=False):
    out = []
    for name, family in families.items():
        if family.get("smoke_only") and not smoke:
            continue
        for level in family["levels"]:
            out.append((name, level))
    return out


def condition_name(family, level):
    return f"{family}_{level}"


def jpeg_bytes(img, q):
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, format="JPEG", quality=int(q), subsampling=2)
    return buf.getvalue()


def jpeg(img, q):
    data = jpeg_bytes(img, q)
    out = np.asarray(Image.open(io.BytesIO(data)).convert("RGB"))
    return out, {"q": int(q), "bytes": len(data)}


def scale(img, s, kernel):
    h, w = img.shape[:2]
    new_w = max(1, round(w * s))
    new_h = max(1, round(h * s))
    out = cv2.resize(img, (new_w, new_h), interpolation=kernels[kernel])
    return out, {"s": s, "kernel": kernel, "w": new_w, "h": new_h, "sx": new_w / w, "sy": new_h / h}


def crop(img, frac, rng):
    h, w = img.shape[:2]
    side = math.sqrt(frac)
    cw = max(8, round(w * side))
    ch = max(8, round(h * side))
    x0 = int(rng.integers(0, w - cw + 1))
    y0 = int(rng.integers(0, h - ch + 1))
    out = np.ascontiguousarray(img[y0 : y0 + ch, x0 : x0 + cw])
    return out, {"frac": frac, "x0": x0, "y0": y0, "w": cw, "h": ch}


def shift(img, k):
    h, w = img.shape[:2]
    out = np.zeros((h + k, w + k, 3), dtype=np.uint8)
    out[k:, k:] = img
    return out, {"k": int(k)}


def letterbox(img, frac):
    h, w = img.shape[:2]
    bar = round(h * frac)
    out = np.zeros((h + 2 * bar, w, 3), dtype=np.uint8)
    out[bar : bar + h] = img
    return out, {"frac": frac, "bar": bar}


def caption(img, frac):
    h, w = img.shape[:2]
    band = max(8, round(h * frac))
    pil = Image.fromarray(img.copy())
    draw = ImageDraw.Draw(pil)
    draw.rectangle([0, h - band, w, h], fill=(20, 20, 20))
    font = ImageFont.load_default(size=max(10, int(band * 0.45)))
    draw.text((w // 40, h - band + band // 4), caption_text, fill=(255, 255, 255), font=font)
    return np.asarray(pil), {"frac": frac, "band": band}


def sticker(img, frac, rng):
    h, w = img.shape[:2]
    side = max(8, round(math.sqrt(frac * h * w)))
    side = min(side, h, w)
    x0 = int(rng.integers(0, w - side + 1))
    y0 = int(rng.integers(0, h - side + 1))
    pil = Image.fromarray(img.copy())
    draw = ImageDraw.Draw(pil)
    box = [x0, y0, x0 + side - 1, y0 + side - 1]
    draw.ellipse(box, fill=(255, 204, 0), outline=(120, 80, 0), width=max(1, side // 40))
    eye = max(2, side // 12)
    for cx in (x0 + side * 0.33, x0 + side * 0.67):
        draw.ellipse([cx - eye, y0 + side * 0.35 - eye, cx + eye, y0 + side * 0.35 + eye], fill=(40, 30, 0))
    draw.arc([x0 + side * 0.25, y0 + side * 0.4, x0 + side * 0.75, y0 + side * 0.8], 20, 160, fill=(40, 30, 0), width=max(2, side // 30))
    return np.asarray(pil), {"frac": frac, "x0": x0, "y0": y0, "side": side}


def brightness(img, f):
    out = np.clip(img.astype(np.float32) * f, 0, 255).round().astype(np.uint8)
    return out, {"f": f}


def contrast(img, f):
    mean = img.astype(np.float32).mean()
    out = np.clip((img.astype(np.float32) - mean) * f + mean, 0, 255).round().astype(np.uint8)
    return out, {"f": f, "mean": float(mean)}


def gamma(img, g):
    out = np.clip(255.0 * (img.astype(np.float32) / 255.0) ** g, 0, 255).round().astype(np.uint8)
    return out, {"g": g}


def rotation_matrix(deg, w, h):
    m = cv2.getRotationMatrix2D(((w - 1) / 2, (h - 1) / 2), deg, 1.0)
    return np.vstack([m, [0, 0, 1]])


def rotate(img, cover, deg):
    h, w = img.shape[:2]
    m = rotation_matrix(deg, w, h)[:2]
    turned = cv2.warpAffine(img, m, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    inside = cv2.warpAffine(np.full((h, w), 255, np.uint8), m, (w, h), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0) > 0
    out = np.where(inside[:, :, None], turned, cover)
    return out, {"deg": deg}


def apply(family, level, img, cover, rng):
    kind = families[family]["kind"]
    if kind == "jpeg":
        return jpeg(img, level)
    if kind == "scale":
        return scale(img, level, families[family]["kernel"])
    if kind == "crop":
        return crop(img, level, rng)
    if kind == "shift":
        return shift(img, level)
    if kind == "letterbox":
        return letterbox(img, level)
    if kind == "caption":
        return caption(img, level)
    if kind == "sticker":
        return sticker(img, level, rng)
    if kind == "brightness":
        return brightness(img, level)
    if kind == "contrast":
        return contrast(img, level)
    if kind == "gamma":
        return gamma(img, level)
    return rotate(img, cover, level)


def translation(dx, dy):
    return np.array([[1.0, 0.0, dx], [0.0, 1.0, dy], [0.0, 0.0, 1.0]])


def scaling(sx, sy):
    return np.array([[sx, 0.0, (sx - 1) / 2], [0.0, sy, (sy - 1) / 2], [0.0, 0.0, 1.0]])


def inverse(family, params, shape):
    h, w = shape[:2]
    kind = families[family]["kind"]
    valid = np.ones((h, w), dtype=bool)
    if kind == "scale":
        return scaling(params["sx"], params["sy"]), valid
    if kind == "crop":
        valid[:] = False
        valid[params["y0"] : params["y0"] + params["h"], params["x0"] : params["x0"] + params["w"]] = True
        return translation(-params["x0"], -params["y0"]), valid
    if kind == "shift":
        return translation(params["k"], params["k"]), valid
    if kind == "letterbox":
        return translation(0, params["bar"]), valid
    if kind == "caption":
        valid[h - params["band"] :] = False
        return np.eye(3), valid
    if kind == "sticker":
        valid[params["y0"] : params["y0"] + params["side"], params["x0"] : params["x0"] + params["side"]] = False
        return np.eye(3), valid
    if kind == "rotate":
        m = rotation_matrix(params["deg"], w, h)
        ys, xs = np.mgrid[0:h, 0:w]
        fx = m[0, 0] * xs + m[0, 1] * ys + m[0, 2]
        fy = m[1, 0] * xs + m[1, 1] * ys + m[1, 2]
        valid = (fx >= 0) & (fx <= w - 1) & (fy >= 0) & (fy <= h - 1)
        return m, valid
    return np.eye(3), valid
