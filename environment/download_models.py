import argparse
from pathlib import Path

import yaml

from wmbench.fetch import fetch_file

root = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    config = yaml.safe_load((root / "configs" / "models.yaml").read_text())
    for model in config["models"]:
        dest = Path(args.root) / model["dest"]
        got = fetch_file(model["url"], dest, model.get("sha256"))
        print(model["name"], dest, got)
    print("models", len(config["models"]))


if __name__ == "__main__":
    main()
