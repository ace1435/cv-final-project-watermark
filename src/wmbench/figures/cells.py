import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from statsmodels.stats.proportion import proportion_confint

from wmbench.detect.thresholds import load_family_thresholds, load_thresholds
from wmbench.transforms import screenshots
from wmbench.transforms.registry import conditions
from wmbench.watermarkers import primaries

rungs = [1, 2, 3]
labels = ["survived", "alignment", "recoverable", "sync_failed", "destroyed"]


def read_records(paths):
    out = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    out.append(json.loads(line))
    return out


def wilson(count, n):
    if n == 0:
        return float("nan"), float("nan")
    low, high = proportion_confint(count, n, alpha=0.05, method="wilson")
    return float(low), float(high)


def detected(record, tau):
    return record["score"] >= tau


def group_by_item(records):
    items = defaultdict(dict)
    for r in records:
        rung = r["rung"]
        if rung in ("2z",):
            items[(r["image"], r["method"], r["condition"])]["2z"] = r
        else:
            items[(r["image"], r["method"], r["condition"])][int(rung)] = r
    return items


def label_of(item, tau, tau3):
    d1 = detected(item[1], tau)
    d2 = detected(item[2], tau)
    d3 = detected(item[3], tau3) if 3 in item else None
    if d1:
        return "survived"
    if d2 and d3:
        return "recoverable"
    if d2 and d3 is False:
        return "sync_failed"
    if d2:
        return "alignment"
    return "destroyed"


def condition_order(smoke):
    return [(c.name, c.family, c.level) for c in conditions(["tier1", "platform", "platform_hires", "screenshot", "chain"], smoke)]


def cell_rows(records, thresholds, thresholds3, smoke, domains=("all", "photo", "screen"), family_thresholds=None):
    family_thresholds = family_thresholds or {}
    items = group_by_item(records)
    order = condition_order(smoke)
    rows = []
    for name, family, level in order:
        for method in primaries:
            tau = thresholds[method]
            tau3 = thresholds3.get(method, tau)
            for domain in domains:
                mine = [it for (img, m, c), it in items.items() if m == method and c == name and 1 in it and 2 in it and (domain == "all" or it[1]["domain"] == domain)]
                if not mine:
                    continue
                row = {"condition": name, "family": family, "level": level, "method": method, "domain": domain, "n": len(mine)}
                for rung in rungs:
                    have = [it for it in mine if rung in it]
                    if not have:
                        continue
                    t = tau3 if rung == 3 else tau
                    hits = sum(detected(it[rung], t) for it in have)
                    low, high = wilson(hits, len(have))
                    row[f"tpr_r{rung}"] = hits / len(have)
                    row[f"tpr_r{rung}_low"] = low
                    row[f"tpr_r{rung}_high"] = high
                    row[f"bitacc_r{rung}"] = float(np.mean([it[rung]["bitacc"] for it in have]))
                    tf = family_thresholds.get((method, family, rung))
                    if tf is not None:
                        row[f"tau_family_r{rung}"] = tf
                        row[f"tpr_family_r{rung}"] = sum(detected(it[rung], tf) for it in have) / len(have)
                marked = [str(r) for r in rungs if (method, family, r) in family_thresholds]
                if marked:
                    row["recalibrated_rungs"] = " ".join(marked)
                if all("2z" in it for it in mine):
                    hits = sum(detected(it["2z"], tau) for it in mine)
                    row["tpr_r2_zero_fill"] = hits / len(mine)
                counts = defaultdict(int)
                for it in mine:
                    counts[label_of(it, tau, tau3)] += 1
                for lab in labels:
                    row[f"label_{lab}"] = counts[lab] / len(mine)
                row["valid_fraction"] = float(np.mean([it[2]["valid_fraction"] for it in mine]))
                threes = [it[3] for it in mine if 3 in it]
                if threes:
                    row["corner_error_median"] = float(np.median([t["corner_error"] for t in threes]))
                    row["reg_failed"] = float(np.mean([t["reg_method"] == "failed" for t in threes]))
                rows.append(row)
    return rows


def write_csv(path, rows):
    path = Path(path)
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
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else row.get(k, "")) for k, v in ((k, row.get(k, "")) for k in keys)})


def folder_of(family):
    if family in ("telegram_std", "twitter", "whatsapp_android", "instagram", "facebook"):
        return "platform"
    if family.startswith("chain_"):
        return "chains"
    if family in screenshots.conditions:
        return "screenshot"
    if family.startswith("downscale_"):
        return "downscale"
    return family


def split_by_folder(rows):
    out = defaultdict(list)
    for row in rows:
        folder = folder_of(row["family"])
        if row["condition"].startswith("platform_hires_"):
            folder = "platform_hires"
        elif row["family"] in ("telegram_std", "twitter", "whatsapp_android", "instagram", "facebook") and row["condition"] != row["family"]:
            folder = "platform"
        out[folder].append(row)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", nargs="+", required=True)
    parser.add_argument("--thresholds", default="results/summary/thresholds.csv")
    parser.add_argument("--thresholds3", default="")
    parser.add_argument("--thresholds-family", default="")
    parser.add_argument("--out-dir", default="results")
    parser.add_argument("--tag", default="smoke")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    thresholds = load_thresholds(args.thresholds)
    thresholds3 = load_thresholds(args.thresholds3) if args.thresholds3 else {}
    family = load_family_thresholds(args.thresholds_family) if args.thresholds_family else {}
    records = read_records(args.records)
    rows = cell_rows(records, thresholds, thresholds3, args.smoke, family_thresholds=family)
    out = Path(args.out_dir)
    write_csv(out / "summary" / f"cells_{args.tag}.csv", rows)
    for folder, mine in split_by_folder(rows).items():
        write_csv(out / folder / f"cells_{args.tag}.csv", mine)
    pooled = [r for r in rows if r["domain"] == "all"]
    for method in primaries:
        mine = [r for r in pooled if r["method"] == method and "tpr_r3" in r]
        if mine:
            print(f"{method:12s} conditions {len(mine)} mean tpr r1 {np.mean([r['tpr_r1'] for r in mine]):.3f} r2 {np.mean([r['tpr_r2'] for r in mine]):.3f} r3 {np.mean([r['tpr_r3'] for r in mine]):.3f}")


if __name__ == "__main__":
    main()
