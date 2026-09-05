import base64
import hashlib
import io
import json
import math
from pathlib import Path

import cv2
import numpy as np
import yaml
from PIL import Image

from wmbench.transforms.tier1 import jpeg, scaling, translation

root = Path(__file__).resolve().parents[3]
config = yaml.safe_load((root / "configs" / "screenshots.yaml").read_text(encoding="utf-8"))
conditions = config["conditions"]
margin = config["margin_css"]
no_resample_band = 0.025

_renderer = None


def get_renderer():
    global _renderer
    if _renderer is None:
        _renderer = renderer()
    return _renderer


def png_data_url(img):
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def layout(img, cond):
    h, w = img.shape[:2]
    if "phone_width" in cond:
        css_w = int(cond["phone_width"])
        left = 0
    else:
        css_w = int(round(w * cond.get("fit", 1.0)))
        left = margin
    css_h = int(round(h * css_w / w))
    return css_w, css_h, left, margin


class renderer:
    def __init__(self):
        from playwright.sync_api import sync_playwright

        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(args=list(config["chromium_args"]))
        self.version = self.browser.version

    def close(self):
        self.browser.close()
        self.pw.stop()

    def capture(self, img, cond):
        css_w, css_h, left, top = layout(img, cond)
        view_w = css_w + 2 * left
        view_h = css_h + 2 * top
        scale = cond["dpr"] * cond["zoom"]
        context = self.browser.new_context(viewport={"width": view_w, "height": view_h}, device_scale_factor=scale, is_mobile=bool(cond.get("mobile", False)))
        page = context.new_page()
        style = f"display:block;position:absolute;left:{left}px;top:{top}px;width:{css_w}px;height:{css_h}px"
        html = f'<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>*{{animation:none !important;transition:none !important}}</style></head><body style="margin:0;background:#fff"><img id="im" src="{png_data_url(img)}" loading="eager" style="{style}"></body></html>'
        page.set_content(html)
        page.evaluate("document.getElementById('im').decode()")
        rect = page.evaluate("JSON.stringify(document.getElementById('im').getBoundingClientRect())")
        dpr = page.evaluate("window.devicePixelRatio")
        fmt = cond.get("format", "png")
        if fmt == "jpeg":
            data = page.screenshot(scale="device", type="jpeg", quality=int(cond.get("quality", 80)), animations="disabled")
        else:
            data = page.screenshot(scale="device", type="png", animations="disabled")
        context.close()
        shot = np.asarray(Image.open(io.BytesIO(data)).convert("RGB"))
        r = json.loads(rect)
        box = [int(round(r["left"] * dpr)), int(round(r["top"] * dpr)), int(round(r["width"] * dpr)), int(round(r["height"] * dpr))]
        return shot, box, dpr, {"css_w": css_w, "css_h": css_h, "view_w": view_w, "view_h": view_h, "left": left, "top": top}


def partial_box(dev_w, dev_h, frac, rng):
    side = math.sqrt(frac)
    pw = max(8, int(round(dev_w * side)))
    ph = max(8, int(round(dev_h * side)))
    x0 = int(rng.integers(0, dev_w - pw + 1))
    y0 = int(rng.integers(0, dev_h - ph + 1))
    return {"x0": x0, "y0": y0, "w": pw, "h": ph}


def render(name, img, rng):
    cond = conditions[name]
    shot, box, dpr, extra = get_renderer().capture(img, cond)
    x0, y0, bw, bh = box
    out = shot[y0 : y0 + bh, x0 : x0 + bw]
    params = {"condition": name, "zoom": cond["zoom"], "dpr": cond["dpr"], "dpr_js": dpr, "fit": cond.get("fit", 1.0), "dev_box": box, "format": cond.get("format", "png"), "quality": cond.get("quality"), "chromium": get_renderer().version}
    params.update(extra)
    h, w = img.shape[:2]
    params["sx"] = extra["css_w"] * dpr / w
    params["sy"] = extra["css_h"] * dpr / h
    params["phase_x"] = extra["left"] * dpr - x0
    params["phase_y"] = extra["top"] * dpr - y0
    if "partial" in cond:
        p = partial_box(bw, bh, cond["partial"], rng)
        out = out[p["y0"] : p["y0"] + p["h"], p["x0"] : p["x0"] + p["w"]]
        params["partial"] = p
    return np.ascontiguousarray(out), params


def forward_matrix(params):
    matrix = scaling(params["sx"], params["sy"])
    return translation(params["phase_x"], params["phase_y"]) @ matrix


def inverse(params, shape):
    h, w = shape[:2]
    matrix = forward_matrix(params)
    valid = np.ones((h, w), dtype=bool)
    if params.get("partial"):
        p = params["partial"]
        matrix = translation(-p["x0"], -p["y0"]) @ matrix
        ys, xs = np.mgrid[0:h, 0:w]
        fx = matrix[0, 0] * xs + matrix[0, 2]
        fy = matrix[1, 1] * ys + matrix[1, 2]
        valid = (fx >= 0) & (fx <= p["w"] - 1) & (fy >= 0) & (fy <= p["h"] - 1)
    return matrix, valid


def resample_like_chromium(img, params):
    x0, y0, bw, bh = params["dev_box"]
    s = params["sx"]
    matrix = forward_matrix(params)
    if abs(s - 1) < no_resample_band and (bw, bh) == (img.shape[1], img.shape[0]) and abs(params["phase_x"]) < 1e-6 and abs(params["phase_y"]) < 1e-6:
        return img.copy()
    if abs(s - 1) < no_resample_band:
        return cv2.warpAffine(img, matrix[:2], (bw, bh), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_REPLICATE)
    if s > 0.5:
        return cv2.warpAffine(img, matrix[:2], (bw, bh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    level = int(math.floor(math.log2(1 / s)))
    mip = img
    for i in range(level):
        mip = cv2.resize(mip, (max(1, mip.shape[1] // 2), max(1, mip.shape[0] // 2)), interpolation=cv2.INTER_AREA)
    residual = translation(params["phase_x"], params["phase_y"]) @ scaling(params["sx"] * img.shape[1] / mip.shape[1], params["sy"] * img.shape[0] / mip.shape[0])
    return cv2.warpAffine(mip, residual[:2], (bw, bh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def simulate(img, params):
    out = resample_like_chromium(img, params)
    if params.get("partial"):
        p = params["partial"]
        out = out[p["y0"] : p["y0"] + p["h"], p["x0"] : p["x0"] + p["w"]]
    if params["format"] == "jpeg":
        out, _ = jpeg(np.ascontiguousarray(out), params["quality"])
    return np.ascontiguousarray(out)


def reference_pattern():
    ys, xs = np.mgrid[0:256, 0:256].astype(np.float32)
    r = 40 + 170 * xs / 255
    g = 40 + 170 * ys / 255
    b = 128 + 100 * np.sin(xs / 9) * np.cos(ys / 11)
    img = np.clip(np.stack([r, g, b], axis=-1), 0, 255).astype(np.uint8)
    cv2.circle(img, (128, 128), 60, (255, 255, 255), 3)
    return img


def reference_hash():
    out, params = render("win_125", reference_pattern(), np.random.default_rng(0))
    return hashlib.sha256(out.tobytes()).hexdigest(), params


def check_reference():
    got, params = reference_hash()
    expected = config["reference_hash"]
    return got == expected, got, expected, params["chromium"]
