import argparse
import hashlib
import zipfile
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import pyarrow.parquet as pq
import yaml

from wmbench.fetch import sha256_of
from wmbench.manifest import read_rows, write_rows
from wmbench.prep import prepare, save_png

root = Path(__file__).resolve().parents[1]
config = yaml.safe_load((root / "configs" / "datasets.yaml").read_text(encoding="utf-8"))
long_side = config["long_side"]
dpi = config["render_dpi"]


def out_path(data_root, row):
    return Path(data_root) / row["split"] / f"{row['id']}.png"


def is_pdf(row):
    return row["category"].startswith("doc_")


def iter_tasks(rows, sources_root):
    by_file = defaultdict(list)
    for row in rows:
        by_file[row["file"]].append(row)
    for file in sorted(by_file):
        group = by_file[file]
        path = sources_root / file
        if file.endswith(".zip"):
            with zipfile.ZipFile(path) as z:
                for row in group:
                    yield row, z.read(row["member"])
        elif file.endswith(".parquet"):
            wanted = {int(r["member"]): r for r in group}
            column = "pdf" if is_pdf(group[0]) else "image"
            index = 0
            for batch in pq.ParquetFile(path).iter_batches(batch_size=32, columns=[column]):
                for value in batch.column(0).to_pylist():
                    if index in wanted:
                        yield wanted[index], value if column == "pdf" else value["bytes"]
                    index += 1
        else:
            for row in group:
                yield row, path.read_bytes()


def work(task):
    row, data, dest = task
    got = hashlib.sha256(data).hexdigest()
    if got != row["source_sha256"]:
        raise RuntimeError(f"source sha256 mismatch for {row['id']}")
    img = prepare(data, is_pdf(row), long_side, dpi)
    save_png(img, dest)
    return row["id"], sha256_of(dest)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--data-root", default="data/images")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    rows = read_rows(args.manifest)
    sources_root = Path(args.data_root) / "sources"
    done = {}
    todo = []
    for row in rows:
        dest = out_path(args.data_root, row)
        if dest.exists():
            done[row["id"]] = sha256_of(dest)
        else:
            todo.append(row)
    tasks = ((row, data, out_path(args.data_root, row)) for row, data in iter_tasks(todo, sources_root))
    with Pool(args.workers) as p:
        for i, (key, sha) in enumerate(p.imap_unordered(work, tasks)):
            done[key] = sha
            if (i + 1) % 100 == 0:
                print("processed", i + 1, flush=True)
    changed = 0
    for row in rows:
        sha = done[row["id"]]
        if row["out_sha256"] and row["out_sha256"] != sha:
            changed += 1
            print("changed", row["id"], row["out_sha256"], sha)
        row["out_sha256"] = sha
    write_rows(args.manifest, rows)
    print(f"images {len(rows)} new {len(todo)} existing {len(rows) - len(todo)} changed {changed}")


if __name__ == "__main__":
    main()
