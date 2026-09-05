import argparse
import time
from pathlib import Path

import numpy as np
import yaml
from PIL import Image

from wmbench.detect.analytic import matched_filter, matches
from wmbench.manifest import read_rows
from wmbench.quality.match import match
from wmbench.quality.metrics import psnr, scorer
from wmbench.runner.jobs import run_items
from wmbench.watermarkers import load, primaries
from wmbench.watermarkers.common import root

seeds = yaml.safe_load((root / "configs" / "seeds.yaml").read_text(encoding="utf-8"))


def message_rng(image_id):
    return np.random.default_rng([seeds["message"], int(image_id.rsplit("_", 1)[-1], 16)])


def load_image(data_root, row):
    return np.asarray(Image.open(Path(data_root) / row["split"] / f"{row['id']}.png").convert("RGB"))


def save_marked(data_root, method, point, image_id, marked):
    path = Path(data_root) / "work" / "marked" / method / point / f"{image_id}.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(marked).save(path, format="PNG")


def decode_record(wm, img, bits, prefix, strength=None):
    t0 = time.time()
    scores = wm.decode(img, strength)
    out = {
        f"{prefix}_decode_s": time.time() - t0,
        f"{prefix}_matches": matches(scores, bits),
        f"{prefix}_bitacc": matches(scores, bits) / wm.nbits,
        f"{prefix}_score": matched_filter(scores, bits),
    }
    if hasattr(wm, "ecc_ok"):
        out[f"{prefix}_ecc_ok"] = wm.ecc_ok(scores, bits)
    if hasattr(wm, "pixel_score"):
        out[f"{prefix}_pixel_score"] = wm.pixel_score(img)
    if hasattr(wm, "detect_logit"):
        out[f"{prefix}_detect_logit"] = wm.detect_logit(img)
    return out


def work_item(wm, metrics, data_root, row):
    img = load_image(data_root, row)
    bits = wm.random_bits(message_rng(row["id"]))
    record = {"image": row["id"], "method": wm.name, "domain": row["domain"], "category": row["category"], "nbits": wm.nbits, "bits": "".join(str(int(b)) for b in bits)}
    record.update(decode_record(wm, img, bits, "clean"))
    t0 = time.time()
    native = wm.embed(img, bits, wm.native_strength)
    record["native_embed_s"] = time.time() - t0
    record["native_strength"] = wm.native_strength
    record.update({f"native_{k}": v for k, v in metrics.all(img, native).items()})
    record.update(decode_record(wm, native, bits, "native", wm.native_strength))
    save_marked(data_root, wm.name, "native", row["id"], native)
    t0 = time.time()
    strength, value, matched = match(wm, img, bits)
    record["match_s"] = time.time() - t0
    record["matched_strength"] = strength
    record.update({f"matched_{k}": v for k, v in metrics.all(img, matched).items()})
    record.update(decode_record(wm, matched, bits, "matched", strength))
    save_marked(data_root, wm.name, "matched", row["id"], matched)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--data-root", default="data/images")
    parser.add_argument("--out", required=True)
    parser.add_argument("--methods", nargs="*", default=primaries)
    args = parser.parse_args()
    rows = read_rows(args.manifest)
    metrics = scorer()
    for name in args.methods:
        wm = load(name)
        t0 = time.time()
        finished, skipped = run_items(rows, lambda r: f"{r['id']}|{name}", lambda r: work_item(wm, metrics, args.data_root, r), args.out)
        print(f"{name} finished {finished} skipped {skipped} in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
