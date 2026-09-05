from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from wmbench.manifest import read_rows
from wmbench.watermarkers import load, primaries
from wmbench.watermarkers.common import models_root

root = Path(__file__).resolve().parents[1]
smoke = root / "data" / "images" / "smoke"


def photos():
    manifest = root / "data" / "manifests" / "smoke.csv"
    if not manifest.exists() or not smoke.exists() or not models_root().exists():
        pytest.skip("smoke images or model files not present")
    rows = [r for r in read_rows(manifest) if r["domain"] == "photo"][:5]
    return [np.asarray(Image.open(smoke / f"{r['id']}.png").convert("RGB")) for r in rows]


@pytest.mark.parametrize("name", primaries)
def test_round_trip_on_five_photos(name):
    imgs = photos()
    wm = load(name)
    rng = np.random.default_rng(0)
    for img in imgs:
        bits = wm.random_bits(rng)
        assert bits.shape == (wm.nbits,)
        marked = wm.embed(img, bits, wm.native_strength)
        assert marked.shape == img.shape
        assert marked.dtype == np.uint8
        scores = wm.decode(marked)
        assert scores.shape == (wm.nbits,)
        acc = float(np.mean((scores > 0) == (bits > 0)))
        assert acc >= 0.9
