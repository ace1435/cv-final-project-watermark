import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from wmbench.figures.cells import folder_of, labels
from wmbench.watermarkers import primaries

colors = {"dwtdct": "#7f7f7f", "trustmark_q": "#1f77b4", "wam": "#2ca02c", "pixelseal": "#d62728", "hidden": "#9467bd"}
names = {"dwtdct": "DWT-DCT-SVD", "trustmark_q": "TrustMark", "wam": "Watermark Anything", "pixelseal": "PixelSeal", "hidden": "HiDDeN"}
label_colors = {"survived": "#2ca02c", "alignment": "#ff7f0e", "recoverable": "#1f77b4", "sync_failed": "#9467bd", "destroyed": "#d62728"}
platform_names = ["telegram_std", "twitter", "whatsapp_android", "instagram", "facebook"]
tag_words = {"smoke": "smoke subset, 50 images", "full": "full run, 1,000 images"}


def has(row, key):
    return row.get(key, "") != ""


def read_cells(path):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k, v in r.items():
            if k not in ("condition", "family", "method", "domain") and v != "":
                try:
                    r[k] = float(v)
                except ValueError:
                    pass
    return rows


def save(fig, folder, stem):
    folder.mkdir(parents=True, exist_ok=True)
    fig.savefig(folder / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(folder / f"{stem}.png", bbox_inches="tight", dpi=150)
    plt.close(fig)


def family_folder(row):
    if row["condition"].startswith("platform_hires_"):
        return "platform_hires"
    return folder_of(row["family"])


def level_axis(rows):
    seen = []
    for r in rows:
        key = r["condition"]
        if key not in seen:
            seen.append(key)
    return seen


def curves(rows, folder, metric, title, ylabel, stem):
    conds = level_axis(rows)
    x = np.arange(len(conds))
    fig, ax = plt.subplots(figsize=(max(5, 0.9 * len(conds) + 2), 3.6))
    for method in primaries:
        mine = {r["condition"]: r for r in rows if r["method"] == method}
        if not mine:
            continue
        for rung, style in ((1, "-"), (2, "--")):
            key = f"{metric}_r{rung}"
            if key not in mine[conds[0]]:
                continue
            y = np.array([mine[c][key] for c in conds])
            ax.plot(x, y, style, marker="o", markersize=3, color=colors[method], label=f"{names[method]} rung {rung}")
            if metric == "tpr":
                low = np.array([mine[c][f"tpr_r{rung}_low"] for c in conds])
                high = np.array([mine[c][f"tpr_r{rung}_high"] for c in conds])
                ax.fill_between(x, low, high, color=colors[method], alpha=0.12 if rung == 1 else 0.06)
            family_key = f"tpr_family_r{rung}"
            if metric == "tpr" and all(has(mine[c], family_key) for c in conds):
                y = np.array([mine[c][family_key] for c in conds])
                ax.plot(x, y, ":", marker="x", markersize=4, color=colors[method], label=f"{names[method]} rung {rung}, family threshold")
    ax.set_xticks(x)
    ax.set_xticklabels([c.replace(f"{rows[0]['family']}_", "") if len(conds) > 1 else c for c in conds], rotation=30, ha="right", fontsize=8)
    ax.set_ylim(-0.02, 1.02)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=6, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.22))
    save(fig, folder, stem)


def breakdown(rows, folder, title, stem):
    fig, ax = plt.subplots(figsize=(6, 3.2))
    bottoms = np.zeros(len(primaries))
    for lab in labels:
        values = []
        for method in primaries:
            mine = [r for r in rows if r["method"] == method]
            values.append(np.mean([r[f"label_{lab}"] for r in mine]) if mine else 0)
        values = np.array(values)
        ax.bar([names[m] for m in primaries], values, bottom=bottoms, color=label_colors[lab], label=lab.replace("_", " "))
        bottoms += values
    ax.set_ylim(0, 1)
    ax.set_ylabel("share of images, mean over levels")
    ax.set_title(title, fontsize=10)
    ax.tick_params(axis="x", labelsize=8)
    ax.legend(fontsize=7, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    save(fig, folder, stem)


max_columns = 24


def cell_text(v):
    if abs(round(v, 2)) < 1:
        return f"{v:.2f}".lstrip("0").replace("-0", "-")
    return f"{v:.0f}"


def cell_color(v, diff):
    if diff:
        return "white" if abs(v) > 0.5 else "black"
    return "white" if v < 0.5 else "black"


def heatmap(rows, folder, key, title, stem, diff_key=None):
    conds = level_axis(rows)
    matrix = np.full((len(primaries), len(conds)), np.nan)
    marks = np.full((len(primaries), len(conds)), "", dtype=object)
    family_key = key.replace("tpr_", "tau_family_")
    for i, method in enumerate(primaries):
        for j, cond in enumerate(conds):
            mine = [r for r in rows if r["method"] == method and r["condition"] == cond]
            if mine:
                value = mine[0][key]
                if diff_key:
                    value = value - mine[0][diff_key]
                elif has(mine[0], family_key):
                    marks[i, j] = "*"
                matrix[i, j] = value
    blocks = int(np.ceil(len(conds) / max_columns))
    per = int(np.ceil(len(conds) / blocks))
    fig, axes = plt.subplots(blocks, 1, figsize=(max(8, 0.32 * per + 2), 2.4 * blocks + 0.8), squeeze=False, constrained_layout=True)
    cmap = "RdBu" if diff_key else "viridis"
    vmin, vmax = (-1, 1) if diff_key else (0, 1)
    for b, ax in enumerate(axes[:, 0]):
        start = b * per
        part = matrix[:, start : start + per]
        im = ax.imshow(part, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_yticks(range(len(primaries)))
        ax.set_yticklabels([names[m] for m in primaries], fontsize=8)
        ax.set_xticks(range(part.shape[1]))
        ax.set_xticklabels(conds[start : start + per], rotation=90, fontsize=7)
        for i in range(len(primaries)):
            for j in range(part.shape[1]):
                v = part[i, j]
                if not np.isnan(v):
                    ax.text(j, i, cell_text(v) + marks[i, start + j], ha="center", va="center", fontsize=6.5, color=cell_color(v, diff_key))
    axes[0, 0].set_title(title, fontsize=10)
    fig.colorbar(im, ax=axes[:, 0].tolist(), fraction=0.02, pad=0.01)
    save(fig, folder, stem)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cells", default="results/summary/cells_smoke.csv")
    parser.add_argument("--out-dir", default="results")
    parser.add_argument("--tag", default="smoke")
    args = parser.parse_args()
    rows = [r for r in read_cells(args.cells) if r["domain"] == "all"]
    out = Path(args.out_dir)
    by_folder = defaultdict(list)
    for r in rows:
        by_folder[family_folder(r)].append(r)
    for folder, mine in by_folder.items():
        title = f"{folder}, {tag_words.get(args.tag, args.tag)}, 40 dB point"
        curves(mine, out / folder, "tpr", f"TPR at 1 percent FPR, {title}", "TPR at 1 percent FPR", f"curves_tpr_{args.tag}")
        curves(mine, out / folder, "bitacc", f"bit accuracy, {title}", "bit accuracy", f"curves_bitacc_{args.tag}")
        breakdown(mine, out / folder, f"failure labels, {title}", f"breakdown_{args.tag}")
        print("figures for", folder, len(mine), "rows")
    heatmap(rows, out / "summary", "tpr_r1", f"TPR at 1 percent FPR, rung 1 as received, {args.tag}", f"heatmap_rung1_{args.tag}")
    heatmap(rows, out / "summary", "tpr_r2", f"TPR at 1 percent FPR, rung 2 oracle realigned, {args.tag}", f"heatmap_rung2_{args.tag}")
    heatmap(rows, out / "summary", "tpr_r2", f"rung 2 minus rung 1, alignment recoverable mass, {args.tag}", f"heatmap_diff_{args.tag}", diff_key="tpr_r1")
    heatmap(rows, out / "summary", "tpr_r3", f"TPR at 1 percent FPR, rung 3 estimated realignment, {args.tag}", f"heatmap_rung3_{args.tag}")


if __name__ == "__main__":
    main()
