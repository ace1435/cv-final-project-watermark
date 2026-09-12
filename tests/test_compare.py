import csv

from wmbench.runner.compare_tables import compare
from wmbench.transforms.sweep_table import rows_for


def write(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def test_compare_keys_rows_by_rung(tmp_path):
    rows = [{"method": "wam", "rung": 1, "tau": 3.0}, {"method": "wam", "rung": 3, "tau": 4.7}]
    a = tmp_path / "a.csv"
    b = tmp_path / "b.csv"
    write(a, rows)
    write(b, list(reversed(rows)))
    n_a, n_b, missing, text, worst = compare(a, b, [])
    assert (n_a, n_b, missing, text) == (2, 2, 0, 0)
    assert worst["tau"] == 0.0


def record(rung, matches):
    return {"method": "wam", "condition": "twitter", "family": "twitter", "domain": "photo", "rung": rung, "bitacc": matches / 32, "matches": matches, "params": {"q": 85}}


def test_sweep_counts_only_the_first_rung():
    records = [record(1, 32), record(2, 16), record(3, 16), dict(record(1, 32), domain="screen")]
    rows = rows_for(records)
    row = next(r for r in rows if r["method"] == "wam")
    assert row["n"] == 2
    assert row["bitacc_mean"] == 1.0
