import argparse
import csv
import json
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

from wmbench.detect.analytic import matches, threshold
from wmbench.manifest import read_rows
from wmbench.quality.metrics import psnr
from wmbench.runner.jobs import run_items
from wmbench.runner.robustness import bits_of, load_quality, seeds
from wmbench.transforms import screenshots
from wmbench.transforms.registry import condition_rng
from wmbench.watermarkers import load, primaries


def work_item(wm, quality, data_root, row, name):
    q = quality[(row["id"], wm.name)]
    bits = bits_of(q)
    marked = np.asarray(Image.open(Path(data_root) / "work" / "marked" / wm.name / "matched" / f"{row['id']}.png").convert("RGB"))
    rng = condition_rng(seeds["transform"], row["id"], name)
    t0 = time.time()
    real, params = screenshots.render(name, marked, rng)
    render_s = time.time() - t0
    sim = screenshots.simulate(marked, params)
    tau = threshold(wm.nbits)
    real_scores = wm.decode(real, q["matched_strength"])
    sim_scores = wm.decode(sim, q["matched_strength"])
    real_m = matches(real_scores, bits)
    sim_m = matches(sim_scores, bits)
    return {
        "image": row["id"],
        "method": wm.name,
        "condition": name,
        "domain": row["domain"],
        "params": params,
        "render_s": render_s,
        "psnr_real_sim": psnr(real, sim),
        "real_bitacc": real_m / wm.nbits,
        "sim_bitacc": sim_m / wm.nbits,
        "real_detected": bool(real_m >= tau),
        "sim_detected": bool(sim_m >= tau),
        "same_bits": bool(np.array_equal(real_scores > 0, sim_scores > 0)),
    }


def table(records, out):
    groups = defaultdict(list)
    for r in records:
        groups[(r["condition"], r["method"])].append(r)
    pixel = defaultdict(list)
    for r in records:
        pixel[r["condition"]].append(r["psnr_real_sim"])
    rows = []
    for name in screenshots.conditions:
        for method in primaries:
            group = groups.get((name, method), [])
            if not group:
                continue
            rows.append({
                "condition": name,
                "method": method,
                "n": len(group),
                "psnr_real_sim_mean": np.mean([g["psnr_real_sim"] for g in group]),
                "psnr_real_sim_min": np.min([g["psnr_real_sim"] for g in group]),
                "real_bitacc": np.mean([g["real_bitacc"] for g in group]),
                "sim_bitacc": np.mean([g["sim_bitacc"] for g in group]),
                "bitacc_abs_diff": np.mean([abs(g["real_bitacc"] - g["sim_bitacc"]) for g in group]),
                "real_tpr": np.mean([g["real_detected"] for g in group]),
                "sim_tpr": np.mean([g["sim_detected"] for g in group]),
                "detection_agreement": np.mean([g["real_detected"] == g["sim_detected"] for g in group]),
                "same_bits_rate": np.mean([g["same_bits"] for g in group]),
            })
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in row.items()})
    for row in rows:
        print(f"{row['condition']:18s} {row['method']:12s} psnr {row['psnr_real_sim_mean']:.1f} real {row['real_bitacc']:.3f} sim {row['sim_bitacc']:.3f} agree {row['detection_agreement']:.2f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="data/manifests/smoke.csv")
    parser.add_argument("--data-root", default="data/images")
    parser.add_argument("--quality", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--table", default="results/calibration/screenshots_smoke.csv")
    parser.add_argument("--methods", nargs="*", default=primaries)
    args = parser.parse_args()
    ok, got, expected, chromium = screenshots.check_reference()
    print(f"chromium {chromium} reference hash ok {ok} got {got[:12]} expected {str(expected)[:12]}", flush=True)
    rows = read_rows(args.manifest)
    quality = load_quality(args.quality)
    for name in args.methods:
        wm = load(name)
        items = [(row, cond) for row in rows for cond in screenshots.conditions]
        t0 = time.time()
        finished, skipped = run_items(items, lambda it: f"{it[0]['id']}|{name}|{it[1]}", lambda it: work_item(wm, quality, args.data_root, it[0], it[1]), args.out)
        print(f"{name} finished {finished} skipped {skipped} in {time.time() - t0:.0f}s", flush=True)
    records = [json.loads(line) for line in open(args.out, encoding="utf-8") if line.strip()]
    table(records, args.table)


if __name__ == "__main__":
    main()
