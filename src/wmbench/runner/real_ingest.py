import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

from wmbench.detect.analytic import matched_filter, matches, threshold
from wmbench.runner.jobs import run_items
from wmbench.runner.robustness import load_quality
from wmbench.watermarkers import load, primaries

extensions = {".png", ".jpg", ".jpeg", ".webp", ".heic"}


def parse_name(path):
    stem = path.stem
    parts = stem.split("__")
    if len(parts) < 2:
        return None
    method = parts[0]
    image = parts[1]
    tags = parts[2:] if len(parts) > 2 else []
    return method, image, tags


def scan(folder):
    items = []
    for path in sorted(Path(folder).rglob("*")):
        if path.suffix.lower() not in extensions or path.name == "sheet.csv":
            continue
        parsed = parse_name(path)
        if parsed is None or parsed[0] not in primaries:
            continue
        rel = path.relative_to(folder)
        person = rel.parts[0] if len(rel.parts) > 1 else ""
        device = rel.parts[1] if len(rel.parts) > 2 else ""
        items.append({"path": path, "method": parsed[0], "image": parsed[1], "tags": parsed[2], "person": person, "device": device})
    return items


def load_rgb(path):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    return np.asarray(img.convert("RGB"))


def work_item(wm, quality, item):
    q = quality[(item["image"], wm.name)]
    bits = np.array([int(c) for c in q["bits"]])
    img = load_rgb(item["path"])
    t0 = time.time()
    scores = wm.decode(img, q["matched_strength"])
    return {
        "file": str(item["path"].as_posix()),
        "person": item["person"],
        "device": item["device"],
        "tags": item["tags"],
        "method": wm.name,
        "image": item["image"],
        "width": int(img.shape[1]),
        "height": int(img.shape[0]),
        "decode_s": time.time() - t0,
        "matches": matches(scores, bits),
        "bitacc": matches(scores, bits) / wm.nbits,
        "score": matched_filter(scores, bits),
        "detected_analytic": bool(matches(scores, bits) >= threshold(wm.nbits)),
    }


def summarize(records, out_csv):
    groups = {}
    for r in records:
        key = (r["method"], r["person"], r["device"])
        groups.setdefault(key, []).append(r)
    rows = []
    for (method, person, device), group in sorted(groups.items()):
        rows.append({"method": method, "person": person, "device": device, "n": len(group), "bitacc_mean": f"{np.mean([g['bitacc'] for g in group]):.4f}", "detected_rate": f"{np.mean([g['detected_analytic'] for g in group]):.4f}"})
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["method", "person", "device", "n", "bitacc_mean", "detected_rate"], lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    for row in rows:
        print(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", required=True)
    parser.add_argument("--quality", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()
    items = scan(args.folder)
    print("files recognised", len(items))
    quality = load_quality(args.quality)
    for name in primaries:
        mine = [it for it in items if it["method"] == name]
        if not mine:
            continue
        wm = load(name)
        finished, skipped = run_items(mine, lambda it: it["path"].as_posix(), lambda it: work_item(wm, quality, it), args.out)
        print(f"{name} finished {finished} skipped {skipped}", flush=True)
    records = [json.loads(line) for line in open(args.out, encoding="utf-8") if line.strip()]
    summarize(records, args.summary)


if __name__ == "__main__":
    main()
