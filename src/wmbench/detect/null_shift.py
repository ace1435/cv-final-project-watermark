import argparse
import time
from pathlib import Path

import numpy as np
import yaml
from PIL import Image

from wmbench.detect.analytic import matched_filter, matches
from wmbench.manifest import read_rows
from wmbench.quality.quality_run import message_rng
from wmbench.realign.oracle import realign
from wmbench.runner.jobs import run_items_multi
from wmbench.runner.robustness import decode_at, load_cache, registration
from wmbench.transforms.registry import condition_rng, conditions
from wmbench.watermarkers import load, primaries
from wmbench.watermarkers.common import root

seeds = yaml.safe_load((root / "configs" / "seeds.yaml").read_text(encoding="utf-8"))
representatives = [
    "jpeg_75", "downscale_0.5", "upscale_1.5", "crop_0.5", "shift_8", "letterbox_0.15", "caption_0.1", "sticker_0.1",
    "brightness_0.75", "contrast_0.75", "gamma_0.75", "rotate_3", "telegram_std", "platform_hires_whatsapp_android",
    "desktop_125", "phone_pixel7", "chain_desktop_whatsapp",
]


def pick_conditions():
    by_name = {c.name: c for c in conditions(["tier1", "platform", "platform_hires", "screenshot", "chain"], True)}
    return [by_name[n] for n in representatives]


def work_item(wm, data_root, row, cond, cache, cache_path):
    cover = np.asarray(Image.open(Path(data_root) / row["split"] / f"{row['id']}.png").convert("RGB"))
    bits = wm.random_bits(message_rng(row["id"]))
    rng = condition_rng(seeds["transform"], row["id"], cond.name)
    out, params = cond.apply(cover, cover, rng)
    base = {"image": row["id"], "method": wm.name, "condition": cond.name, "family": cond.family, "domain": row["domain"], "nbits": wm.nbits}
    strength = wm.native_strength
    records = []
    scores = wm.decode(out, strength)
    records.append(dict(base, rung=1, matches=matches(scores, bits), score=matched_filter(scores, bits)))
    oracle, valid = cond.inverse(params, cover.shape)
    back, mask = realign(out, oracle, cover.shape, valid, cover)
    scores, shift = decode_at(wm, back, cover, strength, oracle)
    records.append(dict(base, rung=2, matches=matches(scores, bits), score=matched_filter(scores, bits)))
    est, info, reg_s = registration(cache, cache_path, f"{row['id']}|{cond.name}", cover, out)
    back3, mask3 = realign(out, est, cover.shape, None, cover)
    scores3, shift3 = decode_at(wm, back3, cover, strength, est)
    records.append(dict(base, rung=3, reg_method=info["method"], matches=matches(scores3, bits), score=matched_filter(scores3, bits)))
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="data/manifests/null.csv")
    parser.add_argument("--data-root", default="data/images")
    parser.add_argument("--out", required=True)
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--methods", nargs="*", default=primaries)
    args = parser.parse_args()
    rows = read_rows(args.manifest)
    rng = np.random.default_rng(seeds["sample_null"])
    chosen = [rows[i] for i in sorted(rng.choice(len(rows), size=args.count, replace=False))]
    conds = pick_conditions()
    cache_path = str(Path(args.out).with_suffix(".registration.jsonl"))
    cache = load_cache(cache_path)
    print(f"{len(chosen)} null images, {len(conds)} conditions, cached registrations {len(cache)}", flush=True)
    for name in args.methods:
        wm = load(name)
        items = [(row, cond) for row in chosen for cond in conds]
        t0 = time.time()
        finished, skipped = run_items_multi(items, lambda it: f"{it[0]['id']}|{name}|{it[1].name}", lambda it: work_item(wm, args.data_root, it[0], it[1], cache, cache_path), args.out, 3)
        print(f"{name} finished {finished} skipped {skipped} in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
