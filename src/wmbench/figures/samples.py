import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from wmbench.manifest import read_rows
from wmbench.watermarkers import primaries

gain = 10
panel = 320
labels = ["cover", "native", "residual x10", "matched", "residual x10"]


def residual_view(cover, marked):
    diff = marked.astype(np.float32) - cover.astype(np.float32)
    return np.clip(128 + gain * diff, 0, 255).astype(np.uint8)


def thumb(img):
    pil = Image.fromarray(img)
    pil.thumbnail((panel, panel), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (panel, panel + 18), (255, 255, 255))
    canvas.paste(pil, ((panel - pil.width) // 2, 18))
    return canvas


def strip(cover, native, matched, title):
    panels = [cover, native, residual_view(cover, native), matched, residual_view(cover, matched)]
    out = Image.new("RGB", (panel * len(panels), panel + 36), (255, 255, 255))
    draw = ImageDraw.Draw(out)
    draw.text((4, 2), title, fill=(0, 0, 0))
    for i, (img, label) in enumerate(zip(panels, labels)):
        t = thumb(img)
        out.paste(t, (i * panel, 18))
        draw.text((i * panel + 4, 20), label, fill=(0, 0, 0))
    return out


def pick(rows, count):
    photos = [r for r in rows if r["domain"] == "photo"]
    screens = [r for r in rows if r["domain"] == "screen"]
    return photos[:1] + screens[:1] + screens[-1:] if count == 3 else rows[:count]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="data/manifests/smoke.csv")
    parser.add_argument("--data-root", default="data/images")
    parser.add_argument("--out-dir", default="results/summary/samples")
    parser.add_argument("--count", type=int, default=3)
    args = parser.parse_args()
    rows = pick(read_rows(args.manifest), args.count)
    data = Path(args.data_root)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for method in primaries:
        for row in rows:
            cover = np.asarray(Image.open(data / row["split"] / f"{row['id']}.png").convert("RGB"))
            native = np.asarray(Image.open(data / "work" / "marked" / method / "native" / f"{row['id']}.png").convert("RGB"))
            matched = np.asarray(Image.open(data / "work" / "marked" / method / "matched" / f"{row['id']}.png").convert("RGB"))
            image = strip(cover, native, matched, f"{method} on {row['id']}")
            image.save(out / f"{method}_{row['id']}.png", format="PNG", optimize=True)
            print("wrote", out / f"{method}_{row['id']}.png")


if __name__ == "__main__":
    main()
