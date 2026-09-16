import argparse
import csv
import json
from pathlib import Path

import numpy as np

from wmbench.detect.analytic import threshold
from wmbench.watermarkers import primaries

points = ["native", "matched"]
metrics = ["psnr", "ssim", "lpips", "dists"]
domains = ["photo", "screen", "all"]


def read_records(paths):
    records = {}
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    records[r["key"]] = r
    return list(records.values())


def select(records, method, domain):
    out = [r for r in records if r["method"] == method]
    if domain != "all":
        out = [r for r in out if r["domain"] == domain]
    return out


def summary_rows(records):
    rows = []
    for method in primaries:
        for domain in domains:
            group = select(records, method, domain)
            if not group:
                continue
            nbits = group[0]["nbits"]
            tau = threshold(nbits)
            for point in points:
                row = {"method": method, "domain": domain, "point": point, "n": len(group), "nbits": nbits, "tau_1pct": tau}
                row["strength_mean"] = np.mean([r[f"{point}_strength"] for r in group])
                row["strength_min"] = np.min([r[f"{point}_strength"] for r in group])
                row["strength_max"] = np.max([r[f"{point}_strength"] for r in group])
                for m in metrics:
                    values = [r[f"{point}_{m}"] for r in group]
                    row[f"{m}_mean"] = np.mean(values)
                    row[f"{m}_sd"] = np.std(values)
                    row[f"{m}_min"] = np.min(values)
                row["bitacc_mean"] = np.mean([r[f"{point}_bitacc"] for r in group])
                row["bitacc_min"] = np.min([r[f"{point}_bitacc"] for r in group])
                row["tpr_analytic"] = np.mean([r[f"{point}_matches"] >= tau for r in group])
                row["clean_fpr_analytic"] = np.mean([r["clean_matches"] >= tau for r in group])
                if f"{point}_ecc_ok" in group[0]:
                    row["ecc_ok_rate"] = np.mean([r[f"{point}_ecc_ok"] for r in group])
                if f"{point}_pixel_score" in group[0]:
                    row["pixel_score_mean"] = np.mean([r[f"{point}_pixel_score"] for r in group])
                    row["clean_pixel_score_mean"] = np.mean([r["clean_pixel_score"] for r in group])
                rows.append(row)
    return rows


def timing_rows(records):
    rows = []
    for method in primaries:
        group = select(records, method, "all")
        if not group:
            continue
        rows.append({
            "method": method,
            "n": len(group),
            "embed_s_mean": np.mean([r["native_embed_s"] for r in group]),
            "decode_s_mean": np.mean([r["native_decode_s"] for r in group]),
            "match_s_mean": np.mean([r["match_s"] for r in group]),
        })
    return rows


def per_image_rows(records):
    rows = []
    for r in sorted(records, key=lambda r: (r["method"], r["image"])):
        row = {"method": r["method"], "image": r["image"], "domain": r["domain"], "category": r["category"]}
        for point in points:
            row[f"{point}_strength"] = r[f"{point}_strength"]
            for m in metrics:
                row[f"{point}_{m}"] = r[f"{point}_{m}"]
            row[f"{point}_bitacc"] = r[f"{point}_bitacc"]
        row["clean_bitacc"] = r["clean_bitacc"]
        rows.append(row)
    return rows


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = []
    for row in rows:
        for k in row:
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: fmt(row.get(k, "")) for k in keys})


def fmt(v):
    if isinstance(v, float):
        return f"{v:.4f}"
    return v


def write_tex(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "\\begin{tabular}{llrrrrrrr}",
        "\\toprule",
        "Method & Point & Bits & PSNR & SSIM & LPIPS & DISTS & Bit acc & TPR \\\\",
        "\\midrule",
    ]
    for row in rows:
        if row["domain"] != "all":
            continue
        name = row["method"].replace("_", "\\_")
        lines.append(f"{name} & {row['point']} & {row['nbits']} & {row['psnr_mean']:.1f} & {row['ssim_mean']:.3f} & {row['lpips_mean']:.3f} & {row['dists_mean']:.3f} & {row['bitacc_mean']:.3f} & {row['tpr_analytic']:.2f} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", nargs="+", required=True)
    parser.add_argument("--out-dir", default="results/summary")
    parser.add_argument("--tag", default="smoke")
    parser.add_argument("--machine", default="pc")
    args = parser.parse_args()
    records = read_records(args.records)
    out = Path(args.out_dir)
    rows = summary_rows(records)
    write_csv(out / f"quality_{args.tag}.csv", rows)
    write_csv(out / f"quality_{args.tag}_per_image.csv", per_image_rows(records))
    write_csv(out / f"timing_{args.tag}_{args.machine}.csv", timing_rows(records))
    write_tex(Path("results/tables") / f"quality_{args.tag}.tex", rows)
    for row in rows:
        if row["domain"] == "all":
            print(f"{row['method']:12s} {row['point']:8s} psnr {row['psnr_mean']:.2f} bitacc {row['bitacc_mean']:.3f} tpr {row['tpr_analytic']:.2f} fpr {row['clean_fpr_analytic']:.2f}")


if __name__ == "__main__":
    main()
