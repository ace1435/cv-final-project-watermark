import argparse
import json
import time
from pathlib import Path

import numpy as np
import yaml
from PIL import Image

from wmbench.detect.analytic import matched_filter, matches
from wmbench.manifest import read_rows
from wmbench.runner.jobs import run_items
from wmbench.transforms.registry import condition_rng, conditions
from wmbench.watermarkers import load, primaries
from wmbench.watermarkers.common import root

seeds = yaml.safe_load((root / "configs" / "seeds.yaml").read_text(encoding="utf-8"))


def load_quality(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                out[(r["image"], r["method"])] = r
    return out


def bits_of(record):
    return np.array([int(c) for c in record["bits"]])


def work_item(wm, quality, data_root, point, row, cond):
    q = quality[(row["id"], wm.name)]
    bits = bits_of(q)
    strength = q[f"{point}_strength"]
    cover = np.asarray(Image.open(Path(data_root) / row["split"] / f"{row['id']}.png").convert("RGB"))
    marked = np.asarray(Image.open(Path(data_root) / "work" / "marked" / wm.name / point / f"{row['id']}.png").convert("RGB"))
    rng = condition_rng(seeds["transform"], row["id"], cond.name)
    out, params = cond.apply(marked, cover, rng)
    t0 = time.time()
    scores = wm.decode(out, strength)
    record = {
        "image": row["id"],
        "method": wm.name,
        "point": point,
        "condition": cond.name,
        "family": cond.family,
        "level": cond.level,
        "domain": row["domain"],
        "params": params,
        "out_h": int(out.shape[0]),
        "out_w": int(out.shape[1]),
        "decode_s": time.time() - t0,
        "matches": matches(scores, bits),
        "bitacc": matches(scores, bits) / wm.nbits,
        "score": matched_filter(scores, bits),
    }
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--data-root", default="data/images")
    parser.add_argument("--quality", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--groups", nargs="+", default=["tier1", "platform"])
    parser.add_argument("--point", default="matched")
    parser.add_argument("--methods", nargs="*", default=primaries)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    rows = read_rows(args.manifest)
    quality = load_quality(args.quality)
    conds = conditions(args.groups, args.smoke)
    for name in args.methods:
        wm = load(name)
        items = [(row, cond) for row in rows for cond in conds]
        t0 = time.time()
        finished, skipped = run_items(
            items,
            lambda it: f"{it[0]['id']}|{name}|{args.point}|{it[1].name}",
            lambda it: work_item(wm, quality, args.data_root, args.point, it[0], it[1]),
            args.out,
        )
        print(f"{name} finished {finished} skipped {skipped} in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
