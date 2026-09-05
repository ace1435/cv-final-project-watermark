import numpy as np

from wmbench.transforms import platforms, screenshots, tier1
from wmbench.transforms.tier1 import translation

chains = {
    "chain_desktop_whatsapp": [("screenshot", "win_125"), ("platform", "whatsapp_android")],
    "chain_phone_instagram": [("screenshot", "phone_pixel7"), ("center_crop", (4, 5)), ("platform", "instagram")],
    "chain_crop_jpeg_screenshot": [("tier1", ("crop", 0.7)), ("tier1", ("jpeg", 85)), ("screenshot", "desktop_110")],
    "chain_double_screenshot": [("screenshot", "desktop_110"), ("screenshot", "desktop_90")],
    "chain_telegram_caption_twitter": [("platform", "telegram_std"), ("tier1", ("caption", 0.1)), ("platform", "twitter")],
}


def center_crop(img, aspect):
    h, w = img.shape[:2]
    aw, ah = aspect
    target_h = h
    target_w = int(round(h * aw / ah))
    if target_w > w:
        target_w = w
        target_h = int(round(w * ah / aw))
    x0 = (w - target_w) // 2
    y0 = (h - target_h) // 2
    out = np.ascontiguousarray(img[y0 : y0 + target_h, x0 : x0 + target_w])
    return out, {"x0": x0, "y0": y0, "w": target_w, "h": target_h, "aspect": [aw, ah]}


def apply_step(kind, spec, img, cover, rng):
    if kind == "screenshot":
        return screenshots.render(spec, img, rng)
    if kind == "platform":
        return platforms.apply(spec, img)
    if kind == "center_crop":
        return center_crop(img, spec)
    family, level = spec
    return tier1.apply(family, level, img, cover, rng)


def step_inverse(kind, spec, params, shape):
    h, w = shape[:2]
    if kind == "screenshot":
        return screenshots.inverse(params, shape)
    if kind == "platform":
        return platforms.inverse(params, shape)
    if kind == "center_crop":
        valid = np.zeros((h, w), dtype=bool)
        valid[params["y0"] : params["y0"] + params["h"], params["x0"] : params["x0"] + params["w"]] = True
        return translation(-params["x0"], -params["y0"]), valid
    family, level = spec
    return tier1.inverse(family, params, shape)


def apply(name, img, cover, rng):
    out = img
    steps = []
    for kind, spec in chains[name]:
        shape = list(out.shape[:2])
        out, params = apply_step(kind, spec, out, cover, rng)
        steps.append({"kind": kind, "spec": list(spec) if isinstance(spec, tuple) else spec, "in_shape": shape, "params": params})
    return out, {"chain": name, "steps": steps}


def project_mask(valid_step, cumulative, shape):
    h, w = shape[:2]
    ys, xs = np.mgrid[0:h, 0:w]
    fx = cumulative[0, 0] * xs + cumulative[0, 1] * ys + cumulative[0, 2]
    fy = cumulative[1, 0] * xs + cumulative[1, 1] * ys + cumulative[1, 2]
    ix = np.rint(fx).astype(int)
    iy = np.rint(fy).astype(int)
    sh, sw = valid_step.shape
    inside = (ix >= 0) & (ix < sw) & (iy >= 0) & (iy < sh)
    out = np.zeros((h, w), dtype=bool)
    out[inside] = valid_step[iy[inside], ix[inside]]
    return out


def inverse(params, shape):
    cumulative = np.eye(3)
    valid = np.ones(shape[:2], dtype=bool)
    for step in params["steps"]:
        spec = tuple(step["spec"]) if isinstance(step["spec"], list) else step["spec"]
        matrix, valid_step = step_inverse(step["kind"], spec, step["params"], step["in_shape"])
        valid &= project_mask(valid_step, cumulative, shape)
        cumulative = matrix @ cumulative
    return cumulative, valid
