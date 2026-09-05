import hashlib

import numpy as np

from wmbench.transforms import chains, platforms, screenshots, tier1


class condition:
    def __init__(self, name, family, level, kind):
        self.name = name
        self.family = family
        self.level = level
        self.kind = kind

    def apply(self, img, cover, rng):
        if self.kind == "tier1":
            return tier1.apply(self.family, self.level, img, cover, rng)
        if self.kind == "platform":
            return platforms.apply(self.family, img, self.level)
        if self.kind == "screenshot":
            return screenshots.render(self.family, img, rng)
        return chains.apply(self.family, img, cover, rng)

    def inverse(self, params, shape):
        if self.kind == "tier1":
            return tier1.inverse(self.family, params, shape)
        if self.kind == "platform":
            return platforms.inverse(params, shape)
        if self.kind == "screenshot":
            return screenshots.inverse(params, shape)
        return chains.inverse(params, shape)

    def geometric(self):
        if self.kind == "tier1":
            return tier1.families[self.family]["geometric"]
        return self.kind in ("screenshot", "chain")


def conditions(groups, smoke=False):
    out = []
    if "tier1" in groups:
        for family, level in tier1.conditions(smoke):
            out.append(condition(tier1.condition_name(family, level), family, level, "tier1"))
    if "platform" in groups:
        for name, q in platforms.conditions(smoke):
            out.append(condition(platforms.condition_name(name, q), name, q, "platform"))
    if "screenshot" in groups:
        for name in screenshots.conditions:
            out.append(condition(name, name, None, "screenshot"))
    if "chain" in groups:
        for name in chains.chains:
            out.append(condition(name, name, None, "chain"))
    return out


def condition_rng(seed, image_id, name):
    tag = int(hashlib.sha256(name.encode("utf-8")).hexdigest()[:8], 16)
    return np.random.default_rng([seed, int(image_id.rsplit("_", 1)[-1], 16), tag])
