import numpy as np
import pytest

from wmbench.quality.metrics import psnr
from wmbench.realign.oracle import realign
from wmbench.transforms import platforms, tier1


def smooth_image(h=480, w=640):
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    r = 60 + 90 * np.sin(xs / 90) * np.cos(ys / 70)
    g = 128 + 80 * np.exp(-((xs - 300) ** 2 + (ys - 200) ** 2) / 20000)
    b = 40 + 0.25 * xs + 0.1 * ys
    return np.clip(np.stack([r, g, b], axis=-1), 0, 255).astype(np.uint8)


def masked_psnr(a, b, mask):
    return psnr(a[mask], b[mask])


geometric = [(f, level) for f, level in tier1.conditions(smoke=True) if tier1.families[f]["geometric"]]
flat = [(f, level) for f, level in tier1.conditions(smoke=True) if not tier1.families[f]["geometric"]]


@pytest.mark.parametrize("family,level", geometric)
def test_oracle_inverse_restores_geometry(family, level):
    img = smooth_image()
    rng = np.random.default_rng(3)
    out, params = tier1.apply(family, level, img, img, rng)
    matrix, valid = tier1.inverse(family, params, img.shape)
    back, mask = realign(out, matrix, img.shape, valid)
    assert mask.sum() > 0.2 * mask.size
    inner = mask.copy()
    inner[:4] = inner[-4:] = False
    inner[:, :4] = inner[:, -4:] = False
    assert masked_psnr(img, back, inner) > 45


@pytest.mark.parametrize("family,level", flat)
def test_flat_transforms_keep_size_and_mask_touched_pixels(family, level):
    img = smooth_image()
    rng = np.random.default_rng(3)
    out, params = tier1.apply(family, level, img, img, rng)
    matrix, valid = tier1.inverse(family, params, img.shape)
    assert out.shape == img.shape
    assert np.allclose(matrix, np.eye(3))
    if family in ("caption", "sticker"):
        assert np.array_equal(out[valid], img[valid])
        assert not valid.all()
    else:
        assert valid.all()


def test_crop_records_position_and_shift_moves_content():
    img = smooth_image()
    out, params = tier1.crop(img, 0.5, np.random.default_rng(5))
    assert np.array_equal(out, img[params["y0"] : params["y0"] + params["h"], params["x0"] : params["x0"] + params["w"]])
    shifted, params = tier1.shift(img, 8)
    assert shifted.shape == (img.shape[0] + 8, img.shape[1] + 8, 3)
    assert np.array_equal(shifted[8:, 8:], img)


@pytest.mark.parametrize("name", list(platforms.profiles))
def test_platform_hires_composed_inverse(name):
    img = smooth_image(768, 1024)
    out, params = platforms.apply_hires(name, img)
    limit = platforms.profiles[name]["long_side"]
    assert max(out.shape[:2]) == min(limit, 2048)
    matrix, valid = platforms.inverse_hires(params, img.shape)
    assert abs(matrix[0, 0] - out.shape[1] / img.shape[1]) < 1e-9
    back, mask = realign(out, matrix, img.shape, valid)
    inner = mask.copy()
    inner[:4] = inner[-4:] = False
    inner[:, :4] = inner[:, -4:] = False
    assert masked_psnr(img, back, inner) > 38


def test_platform_profiles_skip_resize_below_limit():
    img = smooth_image(768, 1024)
    for name in platforms.profiles:
        out, params = platforms.apply(name, img)
        assert out.shape == img.shape
        assert params["resized"] is False
        assert params["q"] == platforms.profiles[name]["q"]
    out, params = platforms.apply("instagram", smooth_image(1500, 2000))
    assert params["resized"] is True
    assert max(out.shape[:2]) == 1080
