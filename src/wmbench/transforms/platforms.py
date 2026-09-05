from pathlib import Path

import cv2
import numpy as np
import yaml

from wmbench.transforms.tier1 import jpeg, scaling

root = Path(__file__).resolve().parents[3]
config = yaml.safe_load((root / "configs" / "platforms.yaml").read_text(encoding="utf-8"))
profiles = config["profiles"]
sweep_q = config["sweep_q"]


def conditions(smoke=False):
    out = [(name, None) for name in profiles]
    if smoke:
        for name, profile in profiles.items():
            if profile["confidence"] == "estimate":
                out += [(name, q) for q in sweep_q if q != profile["q"]]
    return out


def condition_name(name, q=None):
    return name if q is None else f"{name}_q{q}"


def apply(name, img, q=None):
    profile = profiles[name]
    h, w = img.shape[:2]
    long_side = max(h, w)
    limit = profile["long_side"]
    params = {"long_side": limit, "resized": False, "sx": 1.0, "sy": 1.0}
    if long_side > limit:
        s = limit / long_side
        new_w = max(1, round(w * s))
        new_h = max(1, round(h * s))
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        params.update({"resized": True, "sx": new_w / w, "sy": new_h / h, "w": new_w, "h": new_h})
    out, jpeg_params = jpeg(img, profile["q"] if q is None else q)
    params.update(jpeg_params)
    return out, params


def inverse(params, shape):
    h, w = shape[:2]
    return scaling(params["sx"], params["sy"]), np.ones((h, w), dtype=bool)
