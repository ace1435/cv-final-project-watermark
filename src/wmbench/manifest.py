import csv
from pathlib import Path

fields = [
    "id",
    "split",
    "domain",
    "category",
    "subcategory",
    "source",
    "file",
    "member",
    "url",
    "license",
    "width",
    "height",
    "source_sha256",
    "out_sha256",
]


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_rows(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})
