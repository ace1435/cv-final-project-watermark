import importlib

registry = {
    "dwtdct": ("wmbench.watermarkers.dwtdct", "dwtdct"),
    "trustmark_q": ("wmbench.watermarkers.trustmark_q", "trustmark_q"),
    "wam": ("wmbench.watermarkers.wam", "wam"),
    "pixelseal": ("wmbench.watermarkers.pixelseal", "pixelseal"),
    "hidden": ("wmbench.watermarkers.hidden", "hidden"),
    "videoseal_1": ("wmbench.watermarkers.pixelseal", "videoseal_1"),
}

primaries = ["dwtdct", "trustmark_q", "wam", "pixelseal", "hidden"]


def load(name):
    module, cls = registry[name]
    return getattr(importlib.import_module(module), cls)()
