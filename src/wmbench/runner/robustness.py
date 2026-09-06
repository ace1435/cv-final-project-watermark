import argparse
import json
import time
from pathlib import Path

import numpy as np
import yaml
from PIL import Image

from wmbench.detect.analytic import matched_filter, matches
from wmbench.manifest import read_rows
from wmbench.realign import estimated
from wmbench.realign.oracle import realign
from wmbench.runner.jobs import run_items_multi
from wmbench.transforms.registry import condition_rng, conditions
from wmbench.watermarkers import load, primaries
from wmbench.watermarkers.common import root

seeds = yaml.safe_load((root / "configs" / "seeds.yaml").read_text(encoding="utf-8"))
all_groups = ["tier1", "platform", "platform_hires", "screenshot", "chain"]
shifts = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]


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


def rolled(img, cover, dx, dy):
    out = np.roll(img, (dy, dx), axis=(0, 1))
    if dy > 0:
        out[:dy] = cover[:dy]
    if dy < 0:
        out[dy:] = cover[dy:]
    if dx > 0:
        out[:, :dx] = cover[:, :dx]
    if dx < 0:
        out[:, dx:] = cover[:, dx:]
    return out


def decode_grid_search(wm, img, cover, strength):
    best = None
    for dx, dy in shifts:
        candidate = rolled(img, cover, dx, dy)
        scores = wm.decode(candidate, strength)
        confidence = float(np.abs(scores).mean())
        if best is None or confidence > best[0]:
            best = (confidence, scores, (dx, dy))
    return best[1], best[2]


def integer_translation(matrix):
    m = np.asarray(matrix)
    linear_ok = np.allclose(m[:2, :2], np.eye(2), atol=1e-6)
    shift_ok = np.allclose(m[:2, 2], np.rint(m[:2, 2]), atol=1e-6)
    return linear_ok and shift_ok


def decode_at(wm, img, cover, strength, matrix):
    if wm.name == "dwtdct" and not integer_translation(matrix):
        return decode_grid_search(wm, img, cover, strength)
    return wm.decode(img, strength), (0, 0)


def shard(spec, items):
    index, count = (int(x) for x in spec.split("/"))
    return items[index::count]


def load_cache(path):
    cache = {}
    path = Path(path)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    cache[r["key"]] = r
    return cache


def registration(cache, path, key, cover, out):
    if key in cache:
        r = cache[key]
        return np.array(r["matrix"]), r["info"], r["register_s"]
    t0 = time.time()
    est, info = estimated.estimate(cover, out)
    record = {"key": key, "matrix": est.tolist(), "info": info, "register_s": time.time() - t0}
    cache[key] = record
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return est, info, record["register_s"]


def score_fields(wm, scores, bits):
    m = matches(scores, bits)
    return {"matches": m, "bitacc": m / wm.nbits, "score": matched_filter(scores, bits)}


def work_item(wm, quality, data_root, point, row, cond, zero_fill, cache, cache_path):
    q = quality[(row["id"], wm.name)]
    bits = bits_of(q)
    strength = q[f"{point}_strength"]
    cover = np.asarray(Image.open(Path(data_root) / row["split"] / f"{row['id']}.png").convert("RGB"))
    marked = np.asarray(Image.open(Path(data_root) / "work" / "marked" / wm.name / point / f"{row['id']}.png").convert("RGB"))
    rng = condition_rng(seeds["transform"], row["id"], cond.name)
    out, params = cond.apply(marked, cover, rng)
    base = {"image": row["id"], "method": wm.name, "point": point, "condition": cond.name, "family": cond.family, "level": cond.level, "domain": row["domain"]}
    records = []
    t0 = time.time()
    scores = wm.decode(out, strength)
    records.append(dict(base, rung=1, params=params, out_h=int(out.shape[0]), out_w=int(out.shape[1]), decode_s=time.time() - t0, **score_fields(wm, scores, bits)))
    oracle, valid = cond.inverse(params, cover.shape)
    t0 = time.time()
    back, mask = realign(out, oracle, cover.shape, valid, cover)
    scores, shift = decode_at(wm, back, cover, strength, oracle)
    records.append(dict(base, rung=2, valid_fraction=float(mask.mean()), shift=list(shift), decode_s=time.time() - t0, **score_fields(wm, scores, bits)))
    if zero_fill:
        back0, mask0 = realign(out, oracle, cover.shape, valid, None)
        scores0, shift0 = decode_at(wm, back0, np.zeros_like(cover), strength, oracle)
        records.append(dict(base, rung="2z", valid_fraction=float(mask0.mean()), shift=list(shift0), **score_fields(wm, scores0, bits)))
    est, info, reg_s = registration(cache, cache_path, f"{row['id']}|{cond.name}", cover, out)
    error = estimated.corner_error(est, oracle, cover.shape)
    back3, mask3 = realign(out, est, cover.shape, None, cover)
    scores3, shift3 = decode_at(wm, back3, cover, strength, est)
    records.append(dict(base, rung=3, reg_method=info["method"], inliers=info["inliers"], ecc=info["ecc"], corner_error=error, register_s=reg_s, valid_fraction=float(mask3.mean()), shift=list(shift3), **score_fields(wm, scores3, bits)))
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--data-root", default="data/images")
    parser.add_argument("--quality", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--groups", nargs="+", default=all_groups)
    parser.add_argument("--point", default="matched")
    parser.add_argument("--methods", nargs="*", default=primaries)
    parser.add_argument("--shard", default="0/1")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--zero-fill", action="store_true")
    parser.add_argument("--registration", default="")
    args = parser.parse_args()
    rows = read_rows(args.manifest)
    quality = load_quality(args.quality)
    conds = conditions(args.groups, args.smoke)
    cache_path = args.registration or str(Path(args.out).with_suffix(".registration.jsonl"))
    cache = load_cache(cache_path)
    print(f"{len(rows)} images, {len(conds)} conditions, methods {args.methods}, cached registrations {len(cache)}", flush=True)
    for name in args.methods:
        wm = load(name)
        items = shard(args.shard, [(row, cond) for row in rows for cond in conds])
        t0 = time.time()
        finished, skipped = run_items_multi(
            items,
            lambda it: f"{it[0]['id']}|{name}|{args.point}|{it[1].name}",
            lambda it: work_item(wm, quality, args.data_root, args.point, it[0], it[1], args.zero_fill, cache, cache_path),
            args.out,
            3,
        )
        print(f"{name} finished {finished} skipped {skipped} in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
