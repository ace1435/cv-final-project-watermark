import numpy as np
import pytest

from wmbench.quality.metrics import psnr
from wmbench.realign.oracle import realign
from wmbench.transforms import chains, screenshots


def smooth_image(h=480, w=640):
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    r = 60 + 90 * np.sin(xs / 90) * np.cos(ys / 70)
    g = 128 + 80 * np.exp(-((xs - 300) ** 2 + (ys - 200) ** 2) / 20000)
    b = 40 + 0.25 * xs + 0.1 * ys
    return np.clip(np.stack([r, g, b], axis=-1), 0, 255).astype(np.uint8)


def browser_available():
    try:
        screenshots.get_renderer()
        return True
    except Exception:
        return False


needs_browser = pytest.mark.skipif(not browser_available(), reason="chromium not available")


@needs_browser
def test_desktop_100_is_bit_exact():
    img = smooth_image(300, 400)
    out, params = screenshots.render("desktop_100", img, np.random.default_rng(0))
    assert out.shape == img.shape
    assert np.array_equal(out, img)
    assert params["sx"] == 1.0


@needs_browser
@pytest.mark.parametrize("name", ["desktop_125", "win_150", "fit_50", "phone_pixel7", "partial_80", "desktop_110_jpeg"])
def test_screenshot_oracle_inverse(name):
    img = smooth_image(300, 400)
    out, params = screenshots.render(name, img, np.random.default_rng(1))
    matrix, valid = screenshots.inverse(params, img.shape)
    back, mask = realign(out, matrix, img.shape, valid)
    assert mask.sum() > 0.5 * mask.size
    inner = mask.copy()
    inner[:4] = inner[-4:] = False
    inner[:, :4] = inner[:, -4:] = False
    assert psnr(img[inner], back[inner]) > 38


@needs_browser
def test_simulation_matches_render_size_and_is_close():
    img = smooth_image(300, 400)
    out, params = screenshots.render("desktop_125", img, np.random.default_rng(0))
    sim = screenshots.simulate(img, params)
    assert sim.shape == out.shape
    assert psnr(out, sim) > 35


@needs_browser
def test_reference_hash_is_stable_within_a_machine():
    a, _ = screenshots.reference_hash()
    b, _ = screenshots.reference_hash()
    assert a == b


@needs_browser
@pytest.mark.parametrize("name", list(chains.chains))
def test_chain_oracle_inverse(name):
    img = smooth_image(300, 400)
    out, params = chains.apply(name, img, img, np.random.default_rng(2))
    matrix, valid = chains.inverse(params, img.shape)
    back, mask = realign(out, matrix, img.shape, valid)
    assert mask.sum() > 0.2 * mask.size
    inner = mask.copy()
    inner[:6] = inner[-6:] = False
    inner[:, :6] = inner[:, -6:] = False
    assert psnr(img[inner], back[inner]) > 33
