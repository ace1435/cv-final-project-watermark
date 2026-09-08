import argparse
import csv
from pathlib import Path


def read(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def as_float(v):
    try:
        return float(v)
    except ValueError:
        return None


def key_of(row, keys):
    return tuple(row.get(k, "") for k in keys)


def compare(a_path, b_path, keys):
    a = read(a_path)
    b = read(b_path)
    if not keys:
        keys = [k for k in a[0] if as_float(a[0][k]) is None]
    b_by = {key_of(r, keys): r for r in b}
    columns = [k for k in a[0] if k not in keys]
    worst = {c: 0.0 for c in columns}
    missing = 0
    text = 0
    for r in a:
        other = b_by.get(key_of(r, keys))
        if other is None:
            missing += 1
            continue
        for c in columns:
            x = as_float(r.get(c, ""))
            y = as_float(other.get(c, ""))
            if x is None or y is None:
                if r.get(c, "") != other.get(c, ""):
                    text += 1
                continue
            worst[c] = max(worst[c], abs(x - y))
    return len(a), len(b), missing, text, worst


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("first")
    parser.add_argument("second")
    parser.add_argument("--keys", nargs="*", default=[])
    parser.add_argument("--tolerance", type=float, default=0.0)
    args = parser.parse_args()
    first = Path(args.first)
    second = Path(args.second)
    pairs = [(first, second)]
    if first.is_dir():
        pairs = [(p, second / p.relative_to(first)) for p in sorted(first.rglob("*.csv")) if (second / p.relative_to(first)).exists()]
    bad = 0
    for a, b in pairs:
        n_a, n_b, missing, text, worst = compare(a, b, args.keys)
        top = max(worst.values()) if worst else 0.0
        flag = "ok" if top <= args.tolerance and missing == 0 and text == 0 else "DIFF"
        if flag == "DIFF":
            bad += 1
        print(f"{flag:4s} {a} rows {n_a} vs {n_b}, unmatched {missing}, text differences {text}, largest numeric difference {top:.6f}")
        for c, v in sorted(worst.items(), key=lambda kv: -kv[1])[:3]:
            if v > args.tolerance:
                print(f"       {c} {v:.6f}")
    print(f"{len(pairs) - bad} of {len(pairs)} tables within tolerance {args.tolerance}")


if __name__ == "__main__":
    main()
