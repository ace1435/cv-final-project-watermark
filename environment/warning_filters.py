import warnings

entries = [
    (
        "torch.jit._serialization",
        "`torch.jit.load` is deprecated",
        "the HiDDeN weights are distributed only as TorchScript files and torch 2.14 still loads them",
    ),
    (
        "torch.jit._script",
        r"`torch\.jit\.\w+` is deprecated",
        "timm 0.9.16, pinned by VideoSeal, calls torch.jit.script and torch.jit.interface at import time and they still work",
    ),
    (
        "timm.models.layers",
        "Importing from timm.models.layers is deprecated",
        "VideoSeal imports layers through the old timm path, which timm 0.9.16 still provides",
    ),
    (
        "torchvision.models._utils",
        "The parameter 'pretrained' is deprecated",
        "lpips 0.1.4 loads its AlexNet backbone with the old argument, which torchvision 0.29 still honours",
    ),
    (
        "torchvision.models._utils",
        "Arguments other than a weight enum or `None` for 'weights' are deprecated",
        "same lpips 0.1.4 call, torchvision maps pretrained=True to the default weights",
    ),
]


def apply():
    warnings.simplefilter("error")
    for library, message, reason in entries:
        warnings.filterwarnings("ignore", message=message, module=library)
