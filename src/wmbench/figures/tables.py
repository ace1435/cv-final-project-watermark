import argparse
import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

from wmbench.figures.captions import folder_key, label_names, read_cells
from wmbench.figures.plots import has, names
from wmbench.watermarkers import primaries

folder_order = ["jpeg", "downscale", "upscale", "crop", "shift", "letterbox", "caption", "sticker", "brightness", "contrast", "gamma", "rotate", "platform", "platform_hires", "screenshot", "chains"]
folder_words = {
    "jpeg": "JPEG",
    "downscale": "Downscale",
    "upscale": "Upscale",
    "crop": "Crop",
    "shift": "Shift",
    "letterbox": "Letterbox",
    "caption": "Caption band",
    "sticker": "Sticker",
    "brightness": "Brightness",
    "contrast": "Contrast",
    "gamma": "Gamma",
    "rotate": "Rotation",
    "platform": "Platform JPEG",
    "platform_hires": "Platform, 2048 px original",
    "screenshot": "Browser screenshot",
    "chains": "Chains",
}


def tex(s):
    return str(s).replace("_", "\\_").replace("%", "\\%")


def table(path, spec, header, body):
    lines = [f"\\begin{{tabular}}{{{spec}}}", "\\toprule", " & ".join(header) + " \\\\", "\\midrule"]
    lines += [" & ".join(cells) + " \\\\" for cells in body]
    lines += ["\\bottomrule", "\\end{tabular}"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def mean(rows, key):
    mine = [r[key] for r in rows if has(r, key)]
    return float(np.mean(mine)) if mine else float("nan")


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def headline(rows, path):
    body = []
    for method in primaries:
        mine = [r for r in rows if r["method"] == method]
        cells = [names[method], f"{len(mine)}"]
        cells += [f"{mean(mine, f'tpr_r{rung}'):.3f}" for rung in (1, 2, 3)]
        cells += [f"{mean(mine, f'label_{lab}'):.3f}" for lab in label_names]
        body.append(cells)
    header = ["Method", "Conditions", "Rung 1", "Rung 2", "Rung 3", "Survived", "Alignment", "Recoverable", "Sync failed", "Destroyed"]
    table(path, "lrrrrrrrrr", header, body)


def by_folder(rows):
    out = defaultdict(list)
    for r in rows:
        out[folder_key(r)].append(r)
    return out


def families(rows, path):
    groups = by_folder(rows)
    body = []
    for folder in folder_order:
        mine = groups.get(folder, [])
        if not mine:
            continue
        cells = [folder_words[folder], f"{len({r['condition'] for r in mine})}"]
        for method in primaries:
            sub = [r for r in mine if r["method"] == method]
            cells.append(f"{mean(sub, 'tpr_r1'):.2f} / {mean(sub, 'tpr_r2'):.2f}")
        body.append(cells)
    header = ["Family", "Conditions"] + [names[m] for m in primaries]
    table(path, "lr" + "r" * len(primaries), header, body)


def domains(rows, path):
    groups = by_folder(rows)
    body = []
    for folder in folder_order:
        mine = groups.get(folder, [])
        if not mine:
            continue
        cells = [folder_words[folder]]
        for method in primaries:
            photo = [r for r in mine if r["method"] == method and r["domain"] == "photo"]
            screen = [r for r in mine if r["method"] == method and r["domain"] == "screen"]
            cells.append(f"{mean(photo, 'tpr_r1'):.2f} / {mean(screen, 'tpr_r1'):.2f}")
        body.append(cells)
    header = ["Family"] + [names[m] for m in primaries]
    table(path, "l" + "r" * len(primaries), header, body)


def conditions(rows, path):
    order = list(dict.fromkeys(r["condition"] for r in rows))
    body = []
    for cond in order:
        cells = [tex(cond)]
        for method in primaries:
            mine = [r for r in rows if r["condition"] == cond and r["method"] == method]
            star = "$^*$" if mine and has(mine[0], "recalibrated_rungs") else ""
            cells.append(f"{mean(mine, 'tpr_r1'):.2f} / {mean(mine, 'tpr_r2'):.2f}{star}")
        body.append(cells)
    header = ["Condition"] + [names[m] for m in primaries]
    table(path, "l" + "r" * len(primaries), header, body)


def thresholds(path_in, path):
    body = []
    for r in read_csv(path_in):
        body.append([names[r["method"]], r["nbits"], f"{float(r['tau_1pct']):.2f}", f"{float(r['fpr_pooled']):.4f}", f"{float(r['fpr_photo']):.4f}", f"{float(r['fpr_screen']):.4f}", r["tau_analytic_bits"], f"{float(r['fpr_analytic_realised']):.4f}"])
    header = ["Method", "Bits", "Threshold", "FPR pooled", "FPR photos", "FPR screens", "Analytic bits", "Analytic FPR"]
    table(path, "lrrrrrrr", header, body)


def thresholds_family(path_in, path):
    body = []
    for r in read_csv(path_in):
        body.append([names[r["method"]], tex(r["family"]), r["rung"], f"{float(r['tau_pooled']):.2f}", f"{float(r['fpr_pooled']):.3f}", f"{float(r['tau_family']):.2f}", f"{float(r['fpr_family']):.3f}", f"{float(r['fpr_family_photo']):.3f}", f"{float(r['fpr_family_screen']):.3f}"])
    header = ["Method", "Family", "Rung", "Pooled threshold", "Pooled FPR", "Family threshold", "Family FPR", "Photos", "Screens"]
    table(path, "llrrrrrrr", header, body)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cells", default="results/summary/cells_full.csv")
    parser.add_argument("--thresholds", default="results/summary/thresholds.csv")
    parser.add_argument("--thresholds-family", default="results/summary/thresholds_family.csv")
    parser.add_argument("--out-dir", default="results/tables")
    parser.add_argument("--tag", default="full")
    args = parser.parse_args()
    out = Path(args.out_dir)
    with open(args.cells, encoding="utf-8") as f:
        every = list(csv.DictReader(f))
    for r in every:
        for k in ("tpr_r1", "tpr_r2", "tpr_r3"):
            if r[k] != "":
                r[k] = float(r[k])
    pooled = read_cells(args.cells)
    headline(pooled, out / f"headline_{args.tag}.tex")
    families(pooled, out / f"families_{args.tag}.tex")
    domains(every, out / f"domains_{args.tag}.tex")
    conditions(pooled, out / f"conditions_{args.tag}.tex")
    thresholds(args.thresholds, out / "thresholds.tex")
    if Path(args.thresholds_family).exists():
        thresholds_family(args.thresholds_family, out / "thresholds_family.tex")
    print("tables written to", out)


if __name__ == "__main__":
    main()
