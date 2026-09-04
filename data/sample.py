import argparse
import hashlib
import json
import random
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow.parquet as pq
import yaml

from wmbench.fetch import hf_url
from wmbench.manifest import read_rows, write_rows
from wmbench.prep import image_size, pdf_size

root = Path(__file__).resolve().parents[1]
manifests = root / "data" / "manifests"
config = yaml.safe_load((root / "configs" / "datasets.yaml").read_text(encoding="utf-8"))
seeds = yaml.safe_load((root / "configs" / "seeds.yaml").read_text(encoding="utf-8"))
long_side = config["long_side"]
dpi = config["render_dpi"]
sources = {s["name"]: s for s in config["sources"]}

test_plan = [
    ("pro", 350),
    ("mobile", 150),
    ("ui_mobile", 100),
    ("ui_desktop_pro", 50),
    ("ui_desktop_v2", 25),
    ("ui_web", 75),
    ("doc_doclaynet", 150),
    ("doc_arxiv", 100),
]
smoke_plan = [
    ("pro", 17),
    ("mobile", 8),
    ("ui_mobile", 5),
    ("ui_desktop_pro", 2),
    ("ui_desktop_v2", 2),
    ("ui_web", 4),
    ("doc_doclaynet", 7),
    ("doc_arxiv", 5),
]
stratified = {"doc_doclaynet"}
null_total = 5000
null_photo = ["pro", "mobile", "div2k"]
null_ui = ["ui_mobile", "ui_desktop_pro", "ui_desktop_v2", "ui_web", "ui_web_v2"]
null_doc = ["doc_doclaynet"]


class pool:
    def __init__(self):
        self.rows = []
        self.seen = set()
        self.stats = defaultdict(Counter)

    def add(self, source, category, subcategory, file, member, url, data, is_pdf=False):
        name = source["name"]
        self.stats[name]["scanned"] += 1
        sha = hashlib.sha256(data).hexdigest()
        if sha in self.seen:
            self.stats[name]["duplicate"] += 1
            return
        w, h = pdf_size(data, dpi) if is_pdf else image_size(data)
        if max(w, h) < long_side:
            self.stats[name]["too_small"] += 1
            return
        self.seen.add(sha)
        self.stats[name]["kept"] += 1
        self.rows.append({
            "id": f"{category}_{sha[:8]}",
            "domain": source["domain"],
            "category": category,
            "subcategory": subcategory,
            "source": name,
            "file": file,
            "member": member,
            "url": url,
            "license": source["license"],
            "width": w,
            "height": h,
            "source_sha256": sha,
        })


def scan_zip(p, source, sources_root):
    with zipfile.ZipFile(sources_root / source["dest"]) as z:
        for name in sorted(z.namelist()):
            if name.lower().endswith(".png"):
                p.add(source, source["category"], "", source["dest"], name, source["url"], z.read(name))
            elif not name.endswith("/"):
                p.stats[source["name"]]["not_png"] += 1


def scan_screenspot_v2(p, source, sources_root):
    base = sources_root / source["dest"]
    groups = {}
    for group, category in [("mobile", "ui_mobile"), ("desktop", "ui_desktop_v2"), ("web", "ui_web_v2")]:
        items = json.loads((base / f"screenspot_{group}_v2.json").read_text(encoding="utf-8"))
        for item in items:
            groups[item["img_filename"]] = (category, item.get("data_source", ""))
    zip_rel = f"{source['dest']}/screenspotv2_image.zip"
    with zipfile.ZipFile(sources_root / zip_rel) as z:
        for name in sorted(z.namelist()):
            key = name.rsplit("/", 1)[-1]
            if key not in groups:
                continue
            category, subcategory = groups[key]
            if not key.lower().endswith(".png"):
                p.stats[source["name"]][f"{category}_jpg"] += 1
                continue
            p.stats[source["name"]][f"{category}_png"] += 1
            p.add(source, category, subcategory, zip_rel, name, hf_url(source["repo"], "screenspotv2_image.zip"), z.read(name))


def scan_screenspot_pro(p, source, sources_root):
    base = sources_root / source["dest"]
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(sources_root).as_posix()
        name = path.relative_to(base).as_posix()
        if path.suffix.lower() != ".png":
            p.stats[source["name"]]["not_png"] += 1
            continue
        p.add(source, source["category"], path.parent.name, rel, "", hf_url(source["repo"], name), path.read_bytes())


def scan_parquet(p, source, sources_root, column, category_fn, sub_fn, is_pdf):
    base = sources_root / source["dest"]
    for path in sorted(base.rglob("*.parquet")):
        rel = path.relative_to(sources_root).as_posix()
        name = path.relative_to(base).as_posix()
        index = 0
        for batch in pq.ParquetFile(path).iter_batches(batch_size=32):
            for item in batch.to_pylist():
                value = item[column]
                if value is not None:
                    data = value if is_pdf else value["bytes"]
                    p.add(source, category_fn(item), sub_fn(item), rel, str(index), hf_url(source["repo"], name), data, is_pdf)
                else:
                    p.stats[source["name"]]["missing"] += 1
                index += 1


def scan_arxiv(p, source, sources_root):
    base = sources_root / source["dest"]
    for path in sorted(base.glob("*.pdf")):
        rel = path.relative_to(sources_root).as_posix()
        url = f"https://export.arxiv.org/pdf/{path.stem}v1"
        p.add(source, source["category"], "", rel, "", url, path.read_bytes(), True)


def build_pool(sources_root):
    p = pool()
    for source in config["sources"]:
        kind = source["kind"]
        name = source["name"]
        if kind == "file":
            scan_zip(p, source, sources_root)
        elif name == "screenspot_v2":
            scan_screenspot_v2(p, source, sources_root)
        elif name == "screenspot_pro":
            scan_screenspot_pro(p, source, sources_root)
        elif name == "visualwebbench":
            scan_parquet(p, source, sources_root, "image", lambda r: "ui_web", lambda r: r["task_type"], False)
        elif name == "doclaynet":
            scan_parquet(p, source, sources_root, "pdf", lambda r: "doc_doclaynet", lambda r: r["metadata"]["doc_category"], True)
        else:
            scan_arxiv(p, source, sources_root)
        print(name, dict(p.stats[name]), flush=True)
    return p


def draw(rows, n, rng, strata):
    rows = sorted(rows, key=lambda r: r["id"])
    if not strata:
        return rng.sample(rows, n)
    groups = defaultdict(list)
    for row in rows:
        groups[row["subcategory"]].append(row)
    keys = sorted(groups)
    out = []
    for i, key in enumerate(keys):
        share = n // len(keys) + (1 if i < n % len(keys) else 0)
        out.extend(rng.sample(groups[key], share))
    return out


def draw_plan(rows, plan, seed):
    rng = random.Random(seed)
    out = []
    for category, n in plan:
        candidates = [r for r in rows if r["category"] == category]
        out.extend(draw(candidates, n, rng, category in stratified))
    return out


def draw_null(rows, taken, seed):
    rng = random.Random(seed)
    free = [r for r in rows if r["id"] not in taken]
    photos = sorted([r for r in free if r["category"] in null_photo], key=lambda r: r["id"])
    ui = [r for r in free if r["category"] in null_ui]
    docs = [r for r in free if r["category"] in null_doc]
    need = null_total - len(photos)
    ui_n = min(len(ui), need // 2)
    doc_n = need - ui_n
    return photos + draw(ui, ui_n, rng, False) + draw(docs, doc_n, rng, False)


def with_split(rows, split):
    return [dict(r, split=split) for r in rows]


def summarize(name, rows):
    counts = Counter((r["domain"], r["category"]) for r in rows)
    print(name, len(rows), {f"{d}/{c}": n for (d, c), n in sorted(counts.items())})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", default="data/images")
    parser.add_argument("--rebuild-pool", action="store_true")
    args = parser.parse_args()
    pool_path = manifests / "pool.csv"
    if args.rebuild_pool or not pool_path.exists():
        p = build_pool(Path(args.data_root) / "sources")
        write_rows(pool_path, p.rows)
        (manifests / "pool_stats.json").write_text(json.dumps(p.stats, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows = read_rows(pool_path)
    test = draw_plan(rows, test_plan, seeds["sample_test"])
    smoke = draw_plan(test, smoke_plan, seeds["sample_smoke"])
    null = draw_null(rows, {r["id"] for r in test}, seeds["sample_null"])
    write_rows(manifests / "test.csv", with_split(test, "test"))
    write_rows(manifests / "smoke.csv", with_split(smoke, "smoke"))
    write_rows(manifests / "null.csv", with_split(null, "null"))
    summarize("pool", rows)
    summarize("test", test)
    summarize("smoke", smoke)
    summarize("null", null)


if __name__ == "__main__":
    main()
