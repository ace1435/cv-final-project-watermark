import argparse
import csv
import time
import urllib.error
import xml.etree.ElementTree as et
from pathlib import Path

import yaml

from wmbench.fetch import fetch_bytes, fetch_file, fetch_json

root = Path(__file__).resolve().parents[1]
manifests = root / "data" / "manifests"
config = yaml.safe_load((root / "configs" / "datasets.yaml").read_text())
ns = {"oai": "http://www.openarchives.org/OAI/2.0/", "arxiv": "http://arxiv.org/OAI/arXiv/"}
pins_path = manifests / "sources.csv"
pin_fields = ["source", "file", "url", "sha256", "size", "license"]


def load_pins():
    pins = {}
    if pins_path.exists():
        with open(pins_path, newline="") as f:
            for row in csv.DictReader(f):
                pins[row["file"]] = row
    return pins


def save_pins(pins):
    with open(pins_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=pin_fields)
        w.writeheader()
        for key in sorted(pins):
            w.writerow(pins[key])


def hf_url(repo, name):
    return f"https://huggingface.co/datasets/{repo}/resolve/main/{name}"


def hf_listing(repo):
    info = fetch_json(f"https://huggingface.co/api/datasets/{repo}?blobs=true")
    return sorted(s["rfilename"] for s in info["siblings"])


def oai_records(source):
    base = "https://export.arxiv.org/oai2"
    url = f"{base}?verb=ListRecords&metadataPrefix=arXiv&set={source['set']}&from={source['from']}&until={source['until']}"
    records = []
    while url:
        tree = et.fromstring(fetch_bytes(url))
        for meta in tree.iterfind(".//arxiv:arXiv", ns):
            title = " ".join(meta.findtext("arxiv:title", "", ns).split())
            records.append({"id": meta.findtext("arxiv:id", "", ns), "license": meta.findtext("arxiv:license", "", ns), "title": title})
        token = tree.findtext(".//oai:resumptionToken", "", ns)
        url = f"{base}?verb=ListRecords&resumptionToken={token}" if token else None
        time.sleep(3)
    return records


def arxiv_candidates(source):
    path = manifests / "arxiv_candidates.csv"
    if path.exists():
        with open(path, newline="") as f:
            return list(csv.DictReader(f))
    records = [r for r in oai_records(source) if r["license"] in source["licenses"]]
    records = sorted(records, key=lambda r: r["id"])[: source["max_candidates"]]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "license", "title"])
        w.writeheader()
        w.writerows(records)
    return records


def plan_files(source):
    kind = source["kind"]
    if kind == "file":
        return [(source["url"], source["dest"])]
    if kind == "hf":
        names = source.get("files")
        if names is None:
            names = [n for n in hf_listing(source["repo"]) if n.startswith(source["prefix"])]
        return [(hf_url(source["repo"], n), f"{source['dest']}/{n}") for n in names]
    return [(f"https://export.arxiv.org/pdf/{r['id']}v1", f"{source['dest']}/{r['id']}.pdf") for r in arxiv_candidates(source)]


def download_source(source, sources_root, pins):
    count = 0
    for url, rel in plan_files(source):
        dest = sources_root / rel
        fresh = not dest.exists()
        pinned = pins.get(rel, {}).get("sha256")
        try:
            got = fetch_file(url, dest, pinned or None)
        except urllib.error.HTTPError as e:
            if source["kind"] != "arxiv":
                raise
            print("skip", rel, e.code, flush=True)
            continue
        pins[rel] = {"source": source["name"], "file": rel, "url": url, "sha256": got, "size": dest.stat().st_size, "license": source["license"]}
        count += 1
        print(rel, got, flush=True)
        if fresh and source["kind"] == "arxiv":
            time.sleep(3)
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", default="data/images")
    parser.add_argument("--only", nargs="*")
    args = parser.parse_args()
    sources_root = Path(args.data_root) / "sources"
    pins = load_pins()
    total = 0
    for source in config["sources"]:
        if args.only and source["name"] not in args.only:
            continue
        total += download_source(source, sources_root, pins)
        save_pins(pins)
    print("files", total)


if __name__ == "__main__":
    main()
