import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from wmbench.detect.thresholds import load_thresholds
from wmbench.figures.plots import names, save
from wmbench.watermarkers import primaries


def read_records(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", default="data/images/work/null_scores.jsonl")
    parser.add_argument("--thresholds", default="results/summary/thresholds.csv")
    parser.add_argument("--out-dir", default="results/summary")
    args = parser.parse_args()
    records = read_records(args.records)
    thresholds = load_thresholds(args.thresholds)
    fig, axes = plt.subplots(1, len(primaries), figsize=(3.2 * len(primaries), 2.8))
    for ax, method in zip(axes, primaries):
        mine = [r for r in records if r["method"] == method]
        photos = np.array([r["score"] for r in mine if r["domain"] == "photo"])
        screens = np.array([r["score"] for r in mine if r["domain"] == "screen"])
        low = min(photos.min(), screens.min())
        high = max(photos.max(), screens.max())
        bins = np.linspace(low, high, 60)
        ax.hist(photos, bins=bins, alpha=0.6, color="#1f77b4", label=f"photos, n {len(photos)}")
        ax.hist(screens, bins=bins, alpha=0.6, color="#ff7f0e", label=f"screens, n {len(screens)}")
        tau = thresholds[method]
        ax.axvline(tau, color="black", linestyle="--", linewidth=1)
        ax.set_title(f"{names[method]}, threshold {tau:.2f}", fontsize=8)
        ax.set_xlabel("detection score on unwatermarked images", fontsize=7)
        ax.tick_params(labelsize=6)
        ax.legend(fontsize=6)
    axes[0].set_ylabel("images")
    save(fig, Path(args.out_dir), "null_scores")
    print("wrote", Path(args.out_dir) / "null_scores.svg")


if __name__ == "__main__":
    main()
