import hashlib

import numpy as np

from wmbench.transforms import platforms, tier1


class condition:
    def __init__(self, name, family, level, kind):
        self.name = name
        self.family = family
        self.level = level
        self.kind = kind

    def apply(self, img, cover, rng):
        if self.kind == "tier1":
            return tier1.apply(self.family, self.level, img, cover, rng)
        return platforms.apply(self.family, img, self.level)

    def inverse(self, params, shape):
        if self.kind == "tier1":
            return tier1.inverse(self.family, params, shape)
        return platforms.inverse(params, shape)

    def geometric(self):
        return self.kind == "tier1" and tier1.families[self.family]["geometric"]


def conditions(groups, smoke=False):
    out = []
    if "tier1" in groups:
        for family, level in tier1.conditions(smoke):
            out.append(condition(tier1.condition_name(family, level), family, level, "tier1"))
    if "platform" in groups:
        for name, q in platforms.conditions(smoke):
            out.append(condition(platforms.condition_name(name, q), name, q, "platform"))
    return out


def condition_rng(seed, image_id, name):
    tag = int(hashlib.sha256(name.encode("utf-8")).hexdigest()[:8], 16)
    return np.random.default_rng([seed, int(image_id.rsplit("_", 1)[-1], 16), tag])
