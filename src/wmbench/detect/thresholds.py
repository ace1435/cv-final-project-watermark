import argparse
import csv
import json
from pathlib import Path

import numpy as np

from wmbench.detect.analytic import realised_fpr, threshold
from wmbench.watermarkers import primaries

fpr_target = 0.01


def read_records(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def quantile_threshold(values, fpr):
    return float(np.quantile(np.asarray(values), 1 - fpr, method="higher"))


def rows_for(records):
    rows = []
    for method in primaries:
        group = [r for r in records if r["method"] == method]
        if not group:
            continue
        scores = np.array([r["score"] for r in group])
        tau = quantile_threshold(scores, fpr_target)
        nbits = group[0]["nbits"]
        tau_a = threshold(nbits, fpr_target)
        row = {"method": method, "nbits": nbits, "n_null": len(group), "tau_1pct": tau, "fpr_pooled": float((scores >= tau).mean())}
        for domain in ["photo", "screen"]:
            sub = np.array([r["score"] for r in group if r["domain"] == domain])
            row[f"n_{domain}"] = len(sub)
            row[f"fpr_{domain}"] = float((sub >= tau).mean()) if len(sub) else float("nan")
        row["null_score_mean"] = float(scores.mean())
        row["null_score_sd"] = float(scores.std())
        matches = np.array([r["matches"] for r in group])
        row["tau_analytic_bits"] = tau_a
        row["fpr_analytic_nominal"] = realised_fpr(nbits, tau_a)
        row["fpr_analytic_realised"] = float((matches >= tau_a).mean())
        row["null_bitacc_mean"] = float(matches.mean() / nbits)
        rows.append(row)
    return rows


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: (f"{v:.5f}" if isinstance(v, float) else v) for k, v in row.items()})


def load_thresholds(path):
    with open(path, encoding="utf-8") as f:
        return {r["method"]: float(r["tau_1pct"]) for r in csv.DictReader(f)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", required=True)
    parser.add_argument("--out", default="results/summary/thresholds.csv")
    args = parser.parse_args()
    rows = rows_for(read_records(args.records))
    write_csv(args.out, rows)
    for row in rows:
        print(f"{row['method']:12s} n {row['n_null']} tau {row['tau_1pct']:.4f} fpr pooled {row['fpr_pooled']:.4f} photo {row['fpr_photo']:.4f} screen {row['fpr_screen']:.4f} | analytic tau {row['tau_analytic_bits']} nominal {row['fpr_analytic_nominal']:.4f} realised {row['fpr_analytic_realised']:.4f}")


if __name__ == "__main__":
    main()
