import argparse
import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

from wmbench.figures.cells import folder_of
from wmbench.figures.plots import has, names
from wmbench.watermarkers import primaries

marker = "## Figures"
label_names = ["survived", "alignment", "recoverable", "sync_failed", "destroyed"]


def read_cells(path):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        if r["domain"] != "all":
            continue
        row = dict(r)
        for k, v in r.items():
            if k not in ("condition", "family", "method", "domain", "recalibrated_rungs") and v != "":
                try:
                    row[k] = float(v)
                except ValueError:
                    pass
        out.append(row)
    return out


def folder_key(row):
    if row["condition"].startswith("platform_hires_"):
        return "platform_hires"
    return folder_of(row["family"])


def rank_line(rows, key):
    means = []
    for method in primaries:
        mine = [r for r in rows if r["method"] == method and has(r, key)]
        if mine:
            means.append((float(np.mean([r[key] for r in mine])), method))
    means.sort(reverse=True)
    return ", ".join(f"{names[m]} {v:.2f}" for v, m in means)


def worst_cell(rows, method, key):
    mine = [r for r in rows if r["method"] == method and has(r, key)]
    if not mine:
        return None
    return min(mine, key=lambda r: r[key])


def gain_line(rows):
    parts = []
    for method in primaries:
        mine = [r for r in rows if r["method"] == method and has(r, "tpr_r2")]
        if mine:
            gain = float(np.mean([r["tpr_r2"] - r["tpr_r1"] for r in mine]))
            parts.append(f"{names[method]} {gain:+.2f}")
    return ", ".join(parts)


def label_line(rows):
    parts = []
    for method in primaries:
        mine = [r for r in rows if r["method"] == method]
        if mine:
            shares = {lab: float(np.mean([r[f"label_{lab}"] for r in mine])) for lab in label_names}
            top = max(shares, key=shares.get)
            parts.append(f"{names[method]} mostly {top.replace('_', ' ')} at {shares[top]:.2f}")
    return ", ".join(parts)


def family_threshold_parts(rows):
    parts = []
    for method in primaries:
        for rung in (1, 2, 3):
            key = f"tpr_family_r{rung}"
            mine = [r for r in rows if r["method"] == method and has(r, key)]
            if mine:
                pooled = float(np.mean([r[f"tpr_r{rung}"] for r in mine]))
                family = float(np.mean([r[key] for r in mine]))
                tau = mine[0][f"tau_family_r{rung}"]
                parts.append(f"{names[method]} at rung {rung} reads {family:.2f} at the family threshold {tau:.2f} against {pooled:.2f} at the pooled threshold")
    return parts


def family_threshold_text(rows):
    parts = family_threshold_parts(rows)
    if not parts:
        return ""
    return (
        " In the null shift check the pooled threshold let more than 2 percent of unwatermarked images through for some cells of this family, so those cells carry a second number at a threshold set on the 500 null images of this family alone, drawn as dotted lines with crosses and stored in the `tau_family` and `tpr_family` columns of the cell table. The pooled number stays the primary one. "
        + ". ".join(parts)
        + "."
    )


def hurt_cells(rows, limit=0.1):
    out = []
    for r in rows:
        if has(r, "tpr_r2") and r["tpr_r2"] - r["tpr_r1"] < -limit:
            out.append(f"{names[r['method']]} at {r['condition']} from {r['tpr_r1']:.2f} to {r['tpr_r2']:.2f}")
    return out


def hurt_text(rows):
    cells = hurt_cells(rows)
    if not cells:
        return " No cell loses more than 0.1 after the oracle."
    return " Cells that lose more than 0.1 after the oracle are " + ", ".join(cells) + ". These are crops decoded by a method that reads the full canvas, where the received crop alone carries the mark and the oracle pastes it onto a canvas of unwatermarked cover pixels that the decoder averages in."


def family_text(folder, rows, tag, n):
    tpr = rank_line(rows, "tpr_r1")
    tpr2 = rank_line(rows, "tpr_r2")
    tpr3 = rank_line(rows, "tpr_r3")
    bitacc = rank_line(rows, "bitacc_r1")
    gain = gain_line(rows)
    labels = label_line(rows)
    lines = [
        marker,
        "",
        f"### curves_tpr_{tag}",
        "",
        f"**What you see.** One line per method, the share of the {n:,} images whose watermark is still detected at 1 percent FPR after each level of this family, from mild on the left to harsh on the right. Solid lines are rung 1, the image as received. Dashed lines are rung 2, after the oracle puts the image back into place. The shaded band is the 95 percent Wilson interval.",
        "",
        "**How to read it.** A line that stays near 1.0 means the method survives this family. A solid line that drops while its dashed line stays high means the watermark is still there and only alignment was lost. Both lines dropping means the watermark was destroyed.",
        "",
        f"**What it means.** Mean TPR over the levels at rung 1 is {tpr}. After the oracle it is {tpr2}. The gain from realignment is {gain}.{hurt_text(rows)}{family_threshold_text(rows)}",
        "",
        f"**What we conclude.** {conclusion(rows)}",
        "",
        f"### curves_bitacc_{tag}",
        "",
        "**What you see.** The same layout with the fraction of message bits read correctly instead of the detection rate.",
        "",
        "**How to read it.** 1.0 is perfect, 0.5 is a coin toss. Bit accuracy moves before detection does, so it shows early damage that the detector still tolerates.",
        "",
        f"**What it means.** Mean bit accuracy over the levels at rung 1 is {bitacc}.",
        "",
        "**What we conclude.** Methods whose bit accuracy sits well above their detection threshold have margin for chains of actions, methods just above it do not.",
        "",
        f"### breakdown_{tag}",
        "",
        "**What you see.** One bar per method, the share of images in each failure label averaged over the levels. Green survived at rung 1. Orange alignment failure, rescued by the oracle. Blue recoverable in practice, rescued by the estimated realignment too. Purple sync estimator failed, rescued only by the oracle. Red data destroyed, not rescued even by the oracle.",
        "",
        "**How to read it.** Read the colours above the green. Orange and blue are failures a practical fixer can repair, red is not.",
        "",
        f"**What it means.** {labels}.",
        "",
        f"**What we conclude.** After the estimated realignment the mean TPR is {tpr3}, which is the practical ceiling for this family without a synchronisation watermark.",
        "",
    ]
    return "\n".join(lines)


def conclusion(rows):
    best = rank_line(rows, "tpr_r1").split(", ")[0]
    worst_names = []
    for method in primaries:
        w = worst_cell(rows, method, "tpr_r1")
        if w is not None and w["tpr_r1"] < 0.5:
            worst_names.append(f"{names[method]} at {w['condition']} with {w['tpr_r1']:.2f}")
    text = f"The strongest method at rung 1 in this family is {best}."
    if worst_names:
        text += " Cells below one half at rung 1 are " + ", ".join(worst_names) + "."
    return text


def star_text(rows):
    starred = sorted({(r["method"], r["family"]) for r in rows if has(r, "recalibrated_rungs")})
    if not starred:
        return ""
    pairs = ", ".join(f"{names[m]} under {f}" for m, f in starred)
    return f" A star after a number marks a cell that also carries a per family threshold in the cell table, because the pooled threshold let more than 2 percent of unwatermarked images through in the null shift check for that family, method and rung. The starred cells are {pairs}, and their second number is in `thresholds_family.csv` and in the `tpr_family` columns."


def summary_text(rows, tag):
    lines = [
        marker,
        "",
        f"### heatmap_rung1_{tag}, heatmap_rung2_{tag}, heatmap_rung3_{tag}",
        "",
        "**What you see.** Methods as rows, every condition as a column, each cell the share of images detected at 1 percent FPR, dark is low and bright is high. Rung 1 is the image as received, rung 2 after the oracle puts it back into place, rung 3 after the estimated realignment.",
        "",
        f"**How to read it.** Scan a row to see where a method breaks. Scan a column to see which methods a condition breaks. Compare the same cell across the three maps to see whether the failure is alignment or destruction.{star_text(rows)}",
        "",
        f"**What it means.** Mean TPR over all conditions at rung 1 is {rank_line(rows, 'tpr_r1')}, at rung 2 {rank_line(rows, 'tpr_r2')}, at rung 3 {rank_line(rows, 'tpr_r3')}.",
        "",
        "**What we conclude.** The gap between rung 1 and rung 2 is the share of failures that are pure alignment and that a synchronisation step could repair.",
        "",
        f"### heatmap_diff_{tag}",
        "",
        "**What you see.** Rung 2 minus rung 1 per cell, blue where realignment rescues detections, white where it changes nothing, red where the oracle lowers the rate.",
        "",
        "**How to read it.** Strong blue columns are the conditions where the watermark survives in the pixels but the decoder loses it. Red cells are the ones where putting the image back hurts, which only happens when the decoder reads the whole canvas and the filled in cover pixels dilute the mark.",
        "",
        f"**What it means.** The mean gain per method is {gain_line(rows)}.{hurt_text(rows)}",
        "",
        "**What we conclude.** The methods and conditions with the largest gain are the ones where a practical synchroniser is worth building.",
        "",
        "### null_scores",
        "",
        "**What you see.** For every method, the distribution of detection scores on the 5,000 unwatermarked null images, photos and screens in different colours, with the 1 percent threshold as a dashed line.",
        "",
        "**How to read it.** The threshold sits where 1 percent of all null images fall to its right. When the two colours are offset, the realised false positive rate differs between photos and screens at that threshold, which is reported in `thresholds.csv`.",
        "",
        "**What it means.** The classical method has a discrete score, so its threshold lands on a tie and its realised rate is 1.66 percent, 2.8 percent on screens. TrustMark, Watermark Anything and HiDDeN score photos and screens differently, with photo rates of 2.2, 1.4 and 0.3 percent at the pooled threshold.",
        "",
        "**What we conclude.** Every TPR in this benchmark is read against a threshold whose realised false positive rate per domain is known, and the per domain table travels with it.",
        "",
    ]
    return "\n".join(lines)


def write_section(path, text):
    path = Path(path)
    old = path.read_text(encoding="utf-8") if path.exists() else f"# {path.parent.name}\n\n"
    if marker in old:
        old = old[: old.index(marker)].rstrip() + "\n\n"
    path.write_text(old + text, encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cells", default="results/summary/cells_smoke.csv")
    parser.add_argument("--out-dir", default="results")
    parser.add_argument("--tag", default="smoke")
    args = parser.parse_args()
    rows = read_cells(args.cells)
    n = int(rows[0]["n"]) if rows else 0
    by_folder = defaultdict(list)
    for r in rows:
        by_folder[folder_key(r)].append(r)
    for folder, mine in by_folder.items():
        write_section(Path(args.out_dir) / folder / "README.md", family_text(folder, mine, args.tag, n))
        print("captions for", folder)
    write_section(Path(args.out_dir) / "summary" / "README.md", summary_text(rows, args.tag))


if __name__ == "__main__":
    main()
