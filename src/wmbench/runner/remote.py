import argparse
import shlex
import subprocess
from pathlib import Path

import yaml

root = Path(__file__).resolve().parents[3]
config = yaml.safe_load((root / "configs" / "remote.yaml").read_text(encoding="utf-8"))


def run(cmd, check=True):
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, check=check)


def ssh(command, check=True):
    return run(["ssh", "-o", "BatchMode=yes", config["host"], command], check=check)


def push(branch):
    work = config["work"]
    run(["git", "push", "-q", config["remote"], f"{branch}:{branch}"])
    steps = [
        f"git -C {work} fetch -q origin",
        f"git -C {work} checkout -q {branch}",
        f"git -C {work} reset -q --hard origin/{branch}",
        f"git -C {work} log -1 --format='%h %s'",
    ]
    ssh(" && ".join(steps))


def launch(name, command):
    log = f"{config['data']}/logs/{name}.log"
    inner = f"cd {config['work']} && . {config['venv']}/bin/activate && {command} > {log} 2>&1"
    ssh(f"tmux new-session -d -s {name} {shlex.quote(inner)}")
    print(f"launched tmux {name} with log {log}")


def pull(remote_path, local_path):
    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
    run(["scp", "-q", "-r", f"{config['host']}:{remote_path}", str(local_path)])


def jobs():
    ssh("uptime; tmux ls 2>/dev/null || echo 'no tmux sessions'")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("push")
    p.add_argument("branch")
    p = sub.add_parser("launch")
    p.add_argument("name")
    p.add_argument("command")
    p = sub.add_parser("pull")
    p.add_argument("remote_path")
    p.add_argument("local_path")
    sub.add_parser("jobs")
    args = parser.parse_args()
    if args.action == "push":
        push(args.branch)
    elif args.action == "launch":
        launch(args.name, args.command)
    elif args.action == "pull":
        pull(args.remote_path, args.local_path)
    else:
        jobs()


if __name__ == "__main__":
    main()
