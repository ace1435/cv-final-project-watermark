import argparse
import json
import shlex
import subprocess
import time
from pathlib import Path


def load_done(path):
    path = Path(path)
    done = set()
    if not path.exists():
        return done
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                done.add(json.loads(line)["key"])
    return done


def append_record(path, record):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


def run_items(items, key_fn, work_fn, path):
    done = load_done(path)
    finished = 0
    skipped = 0
    for item in items:
        key = key_fn(item)
        if key in done:
            skipped += 1
            continue
        record = {"key": key, "time": time.time()}
        record.update(work_fn(item))
        append_record(path, record)
        done.add(key)
        finished += 1
    return finished, skipped


def run_items_multi(items, key_fn, work_fn, path, last):
    done = load_done(path)
    finished = 0
    skipped = 0
    for item in items:
        key = key_fn(item)
        if f"{key}|{last}" in done:
            skipped += 1
            continue
        for record in work_fn(item):
            full = {"key": f"{key}|{record['rung']}", "time": time.time()}
            full.update(record)
            append_record(path, full)
        done.add(f"{key}|{last}")
        finished += 1
    return finished, skipped


def tmux_command(name, command, log):
    inner = f"{command} > {shlex.quote(str(log))} 2>&1"
    return ["tmux", "new-session", "-d", "-s", name, inner]


def launch_tmux(name, command, log):
    Path(log).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(tmux_command(name, command, log), check=True)


def dummy_work(i):
    time.sleep(0.05)
    return {"square": i * i}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("job", choices=["dummy"])
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    items = list(range(args.n))
    finished, skipped = run_items(items, lambda i: f"dummy_{i}", dummy_work, args.out)
    print(f"finished {finished} skipped {skipped}")


if __name__ == "__main__":
    main()
