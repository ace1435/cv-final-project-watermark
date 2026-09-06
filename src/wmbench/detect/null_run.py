import argparse
import time
from pathlib import Path

import numpy as np
from PIL import Image

from wmbench.detect.analytic import matched_filter, matches
from wmbench.manifest import read_rows
from wmbench.quality.quality_run import message_rng
from wmbench.runner.jobs import run_items
from wmbench.watermarkers import load, primaries


def work_item(wm, data_root, row):
    img = np.asarray(Image.open(Path(data_root) / row["split"] / f"{row['id']}.png").convert("RGB"))
    bits = wm.random_bits(message_rng(row["id"]))
    t0 = time.time()
    scores = wm.decode(img, wm.native_strength)
    return {
        "image": row["id"],
        "method": wm.name,
        "domain": row["domain"],
        "category": row["category"],
        "nbits": wm.nbits,
        "decode_s": time.time() - t0,
        "bits": "".join(str(int(b)) for b in bits),
        "scores": [round(float(s), 5) for s in scores],
        "matches": matches(scores, bits),
        "score": matched_filter(scores, bits),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="data/manifests/null.csv")
    parser.add_argument("--data-root", default="data/images")
    parser.add_argument("--out", required=True)
    parser.add_argument("--methods", nargs="*", default=primaries)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()
    rows = read_rows(args.manifest)
    if args.limit:
        rows = rows[: args.limit]
    for name in args.methods:
        wm = load(name)
        t0 = time.time()
        finished, skipped = run_items(rows, lambda r: f"{r['id']}|{name}", lambda r: work_item(wm, args.data_root, r), args.out)
        print(f"{name} finished {finished} skipped {skipped} in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
