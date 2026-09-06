import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from wmbench.detect.thresholds import load_thresholds, quantile_threshold
from wmbench.watermarkers import primaries

fpr_target = 0.01


def read_records(paths):
    out = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    out.append(json.loads(line))
    return out


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: (f"{v:.5f}" if isinstance(v, float) else v) for k, v in row.items()})


def rung3_rows(records):
    rows = []
    for method in primaries:
        scores = np.array([r["score"] for r in records if r["method"] == method and r["rung"] == 3])
        if len(scores) == 0:
            continue
        tau = quantile_threshold(scores, fpr_target)
        photos = np.array([r["score"] for r in records if r["method"] == method and r["rung"] == 3 and r["domain"] == "photo"])
        screens = np.array([r["score"] for r in records if r["method"] == method and r["rung"] == 3 and r["domain"] == "screen"])
        rows.append({"method": method, "n_null": len(scores), "tau_1pct": tau, "fpr_pooled": float((scores >= tau).mean()), "fpr_photo": float((photos >= tau).mean()), "fpr_screen": float((screens >= tau).mean())})
    return rows


def shift_rows(records, thresholds, thresholds3):
    groups = defaultdict(list)
    for r in records:
        groups[(r["condition"], r["method"], r["rung"])].append(r)
    rows = []
    for (condition, method, rung), group in sorted(groups.items(), key=lambda kv: (kv[0][0], primaries.index(kv[0][1]), kv[0][2])):
        tau = thresholds3[method] if rung == 3 else thresholds[method]
        scores = np.array([r["score"] for r in group])
        photos = np.array([r["score"] for r in group if r["domain"] == "photo"])
        screens = np.array([r["score"] for r in group if r["domain"] == "screen"])
        rows.append({
            "condition": condition,
            "family": group[0]["family"],
            "method": method,
            "rung": rung,
            "n": len(group),
            "tau": tau,
            "fpr": float((scores >= tau).mean()),
            "fpr_photo": float((photos >= tau).mean()) if len(photos) else float("nan"),
            "fpr_screen": float((screens >= tau).mean()) if len(screens) else float("nan"),
            "above_2pct": bool((scores >= tau).mean() > 0.02),
        })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", nargs="+", required=True)
    parser.add_argument("--thresholds", default="results/summary/thresholds.csv")
    parser.add_argument("--out-rung3", default="results/summary/thresholds_rung3.csv")
    parser.add_argument("--out-shift", default="results/summary/null_shift.csv")
    args = parser.parse_args()
    records = read_records(args.records)
    thresholds = load_thresholds(args.thresholds)
    r3 = rung3_rows(records)
    write_csv(args.out_rung3, r3)
    thresholds3 = {r["method"]: r["tau_1pct"] for r in r3}
    rows = shift_rows(records, thresholds, thresholds3)
    write_csv(args.out_shift, rows)
    for r in r3:
        print(f"rung 3 {r['method']:12s} n {r['n_null']} tau {r['tau_1pct']:.4f} fpr photo {r['fpr_photo']:.4f} screen {r['fpr_screen']:.4f} (rung 1 tau {thresholds[r['method']]:.4f})")
    flagged = [r for r in rows if r["above_2pct"]]
    print(f"cells above 2 percent FPR: {len(flagged)} of {len(rows)}")
    for r in flagged[:40]:
        print(f"  {r['condition']:32s} {r['method']:12s} rung {r['rung']} fpr {r['fpr']:.3f} photo {r['fpr_photo']:.3f} screen {r['fpr_screen']:.3f}")


if __name__ == "__main__":
    main()
