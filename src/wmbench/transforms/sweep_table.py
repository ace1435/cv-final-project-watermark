import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from wmbench.detect.analytic import threshold
from wmbench.watermarkers import primaries

nbits = {"dwtdct": 32, "trustmark_q": 100, "wam": 32, "pixelseal": 256, "hidden": 48}


def read_records(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def rows_for(records):
    groups = defaultdict(list)
    for r in records:
        groups[(r["method"], r["condition"])].append(r)
    rows = []
    for method in primaries:
        tau = threshold(nbits[method])
        for (m, cond), group in sorted(groups.items()):
            if m != method:
                continue
            q = group[0]["params"]["q"]
            photos = [r for r in group if r["domain"] == "photo"]
            screens = [r for r in group if r["domain"] == "screen"]
            rows.append({
                "method": method,
                "condition": cond,
                "profile": group[0]["family"],
                "q": q,
                "n": len(group),
                "bitacc_mean": np.mean([r["bitacc"] for r in group]),
                "bitacc_photo": np.mean([r["bitacc"] for r in photos]),
                "bitacc_screen": np.mean([r["bitacc"] for r in screens]),
                "tpr_analytic": np.mean([r["matches"] >= tau for r in group]),
                "tpr_photo": np.mean([r["matches"] >= tau for r in photos]),
                "tpr_screen": np.mean([r["matches"] >= tau for r in screens]),
            })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", required=True)
    parser.add_argument("--out", default="results/platform/sweep_smoke.csv")
    args = parser.parse_args()
    rows = rows_for(read_records(args.records))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in row.items()})
    for row in rows:
        print(f"{row['method']:12s} {row['condition']:22s} bitacc {row['bitacc_mean']:.3f} photo {row['bitacc_photo']:.3f} screen {row['bitacc_screen']:.3f} tpr {row['tpr_analytic']:.2f}")


if __name__ == "__main__":
    main()
