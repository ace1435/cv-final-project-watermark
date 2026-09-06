import numpy as np
import pytest

from wmbench.realign import estimated
from wmbench.runner.jobs import run_items_multi
from wmbench.transforms import tier1


def textured_image(h=480, w=640):
    rng = np.random.default_rng(11)
    base = rng.integers(0, 256, (h // 16, w // 16, 3)).astype(np.uint8)
    img = np.kron(base, np.ones((16, 16, 1), np.uint8))
    ys, xs = np.mgrid[0:h, 0:w]
    ring = ((xs - w / 2) ** 2 + (ys - h / 2) ** 2) ** 0.5
    img[(ring > 100) & (ring < 110)] = 255
    return img


def models_available():
    try:
        estimated.models()
        return True
    except Exception:
        return False


needs_models = pytest.mark.skipif(not models_available(), reason="matching weights not available")


@needs_models
@pytest.mark.parametrize("family,level", [("crop", 0.5), ("downscale", 0.5), ("rotate", 3), ("shift", 8)])
def test_estimated_matrix_is_close_to_oracle(family, level):
    img = textured_image()
    out, params = tier1.apply(family, level, img, img, np.random.default_rng(1))
    oracle, valid = tier1.inverse(family, params, img.shape)
    est, info = estimated.estimate(img, out)
    assert info["method"] != "failed"
    assert estimated.corner_error(est, oracle, img.shape) < 1.5


def test_run_items_multi_writes_all_rungs_and_skips(tmp_path):
    path = tmp_path / "r.jsonl"
    calls = []

    def work(i):
        calls.append(i)
        return [{"rung": 1, "v": i}, {"rung": 2, "v": i}, {"rung": 3, "v": i}]

    assert run_items_multi([1, 2], str, work, path, 3) == (2, 0)
    assert run_items_multi([1, 2, 3], str, work, path, 3) == (1, 2)
    assert calls == [1, 2, 3]
    with open(path) as f:
        assert sum(1 for line in f if line.strip()) == 9
