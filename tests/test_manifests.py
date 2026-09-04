from pathlib import Path

import pytest

from wmbench.manifest import read_rows

manifests = Path(__file__).resolve().parents[1] / "data" / "manifests"


def load(name):
    path = manifests / f"{name}.csv"
    if not path.exists():
        pytest.skip(f"{name}.csv not built yet")
    return read_rows(path)


def test_splits_are_disjoint_and_smoke_is_inside_test():
    test = {r["id"] for r in load("test")}
    smoke = {r["id"] for r in load("smoke")}
    null = {r["id"] for r in load("null")}
    assert smoke <= test
    assert not (test & null)
    assert len(test) == 1000
    assert len(smoke) == 50
    assert len(null) >= 5000


def test_ids_unique_and_hashes_filled():
    for name in ["test", "smoke", "null"]:
        rows = load(name)
        ids = [r["id"] for r in rows]
        assert len(ids) == len(set(ids))
        assert all(len(r["source_sha256"]) == 64 for r in rows)
        assert all(r["split"] == name for r in rows)


def test_domain_balance():
    for name, per_domain in [("test", 500), ("smoke", 25)]:
        rows = load(name)
        photos = sum(r["domain"] == "photo" for r in rows)
        screens = sum(r["domain"] == "screen" for r in rows)
        assert (photos, screens) == (per_domain, per_domain)


def test_div2k_only_in_null():
    for name in ["test", "smoke"]:
        assert all(r["category"] != "div2k" for r in load(name))
