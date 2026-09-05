import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wmbench.manifest import read_rows
from wmbench.realign.oracle import realign
from wmbench.transforms import chains, platforms, screenshots, tier1

panel = 240
pad = 4
strip_ids = ["pro_909cf1d0", "ui_mobile_b20fdb69", "doc_arxiv_9db2a8f7"]
method = "trustmark_q"


def thumb(img, label):
    pil = Image.fromarray(img)
    pil.thumbnail((panel, panel), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (panel, panel + 16), (255, 255, 255))
    canvas.paste(pil, ((panel - pil.width) // 2, 16))
    ImageDraw.Draw(canvas).text((3, 1), label, fill=(0, 0, 0))
    return canvas


def row(panels):
    out = Image.new("RGB", (len(panels) * (panel + pad), panel + 16), (255, 255, 255))
    for i, p in enumerate(panels):
        out.paste(p, (i * (panel + pad), 0))
    return out


def mask_view(mask):
    return np.where(mask[:, :, None], 255, 60).astype(np.uint8).repeat(3, axis=2)


def realigned_panels(out, matrix, valid, cover, label):
    back, mask = realign(out, matrix, cover.shape, valid, cover)
    return [thumb(back, label), thumb(mask_view(mask), "valid mask")]


def family_strip(family, cover, marked, rng):
    panels = [thumb(marked, "watermarked")]
    for level in tier1.families[family]["levels"]:
        out, params = tier1.apply(family, level, marked, cover, rng)
        panels.append(thumb(out, tier1.condition_name(family, level)))
    level = tier1.families[family]["levels"][-1]
    out, params = tier1.apply(family, level, marked, cover, rng)
    matrix, valid = tier1.inverse(family, params, cover.shape)
    panels += realigned_panels(out, matrix, valid, cover, f"oracle realigned {level}")
    return row(panels)


def platform_strip(cover, marked):
    panels = [thumb(marked, "watermarked")]
    for name in platforms.profiles:
        out, params = platforms.apply(name, marked)
        panels.append(thumb(out, f"{name} q{params['q']}"))
    return row(panels)


def screenshot_strips(cover, marked, rng):
    names = list(screenshots.conditions)
    first = [thumb(marked, "watermarked")]
    second = []
    for i, name in enumerate(names):
        out, params = screenshots.render(name, marked, rng)
        (first if i < 8 else second).append(thumb(out, f"{name} {out.shape[1]}x{out.shape[0]}"))
    out, params = screenshots.render("partial_80", marked, rng)
    matrix, valid = screenshots.inverse(params, cover.shape)
    second += realigned_panels(out, matrix, valid, cover, "partial_80 realigned")
    return row(first), row(second)


def chain_strip(cover, marked, rng):
    panels = [thumb(marked, "watermarked")]
    for name in chains.chains:
        out, params = chains.apply(name, marked, cover, rng)
        panels.append(thumb(out, f"{name.replace('chain_', '')} {out.shape[1]}x{out.shape[0]}"))
    out, params = chains.apply("chain_phone_instagram", marked, cover, rng)
    matrix, valid = chains.inverse(params, cover.shape)
    panels += realigned_panels(out, matrix, valid, cover, "phone_instagram realigned")
    return row(panels)


def save(image, folder, name):
    folder.mkdir(parents=True, exist_ok=True)
    image.save(folder / name, format="PNG", optimize=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="data/manifests/smoke.csv")
    parser.add_argument("--data-root", default="data/images")
    parser.add_argument("--out-dir", default="results")
    parser.add_argument("--groups", nargs="+", default=["tier1", "platform", "screenshot", "chain"])
    args = parser.parse_args()
    data = Path(args.data_root)
    out_root = Path(args.out_dir)
    rows = {r["id"]: r for r in read_rows(args.manifest)}
    for image_id in strip_ids:
        cover = np.asarray(Image.open(data / rows[image_id]["split"] / f"{image_id}.png").convert("RGB"))
        marked = np.asarray(Image.open(data / "work" / "marked" / method / "matched" / f"{image_id}.png").convert("RGB"))
        rng = np.random.default_rng([7, int(image_id.rsplit("_", 1)[-1], 16)])
        if "tier1" in args.groups:
            for family in tier1.families:
                if not tier1.families[family].get("smoke_only"):
                    save(family_strip(family, cover, marked, rng), out_root / family / "samples", f"{family}_{image_id}.png")
        if "platform" in args.groups:
            save(platform_strip(cover, marked), out_root / "platform" / "samples", f"platform_{image_id}.png")
        if "screenshot" in args.groups:
            a, b = screenshot_strips(cover, marked, rng)
            save(a, out_root / "screenshot" / "samples", f"screenshot_a_{image_id}.png")
            save(b, out_root / "screenshot" / "samples", f"screenshot_b_{image_id}.png")
        if "chain" in args.groups:
            save(chain_strip(cover, marked, rng), out_root / "chains" / "samples", f"chains_{image_id}.png")
        print("wrote strips for", image_id, flush=True)


if __name__ == "__main__":
    main()
