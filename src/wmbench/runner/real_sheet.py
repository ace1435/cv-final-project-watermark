import argparse
import csv
import shutil
from pathlib import Path

from wmbench.manifest import read_rows
from wmbench.watermarkers import primaries

per_domain = 10


def pick(rows):
    photos = [r for r in rows if r["domain"] == "photo"][:per_domain]
    screens = [r for r in rows if r["domain"] == "screen"][:per_domain]
    return photos + screens


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="data/manifests/smoke.csv")
    parser.add_argument("--data-root", default="data/images")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    rows = pick(read_rows(args.manifest))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    listing = []
    for method in primaries:
        for row in rows:
            name = f"{method}__{row['id']}.png"
            src = Path(args.data_root) / "work" / "marked" / method / "matched" / f"{row['id']}.png"
            shutil.copyfile(src, out / name)
            listing.append({"file": name, "method": method, "image": row["id"], "domain": row["domain"]})
    with open(out / "sheet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["file", "method", "image", "domain"], lineterminator="\n")
        w.writeheader()
        w.writerows(listing)
    print("sheet files", len(listing), "in", out)


if __name__ == "__main__":
    main()
