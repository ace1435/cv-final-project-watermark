import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

agent = {"User-Agent": "wmbench/0.1 (research benchmark)"}


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def open_url(url, headers=None, tries=5):
    merged = dict(agent)
    merged.update(headers or {})
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=merged)
            return urllib.request.urlopen(req, timeout=120)
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and i + 1 < tries:
                wait = int(e.headers.get("Retry-After", "10"))
                time.sleep(wait)
                continue
            raise


def fetch_bytes(url):
    with open_url(url) as r:
        return r.read()


def fetch_json(url):
    return json.loads(fetch_bytes(url).decode("utf-8"))


def fetch_file(url, dest, sha256=None):
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        got = sha256_of(dest)
        if sha256 is None or got == sha256:
            return got
        dest.unlink()
    part = dest.with_name(dest.name + ".part")
    start = part.stat().st_size if part.exists() else 0
    headers = {"Range": f"bytes={start}-"} if start else {}
    with open_url(url, headers) as r:
        mode = "ab" if r.status == 206 else "wb"
        with open(part, mode) as f:
            for chunk in iter(lambda: r.read(1 << 20), b""):
                f.write(chunk)
    got = sha256_of(part)
    if sha256 is not None and got != sha256:
        part.unlink()
        raise RuntimeError(f"sha256 mismatch for {url}, got {got}")
    part.replace(dest)
    return got
