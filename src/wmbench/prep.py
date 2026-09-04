import hashlib
import io

import pymupdf
from PIL import Image, ImageOps

png_meta_chunks = (b"gAMA", b"iCCP", b"cHRM", b"sRGB", b"pHYs", b"eXIf")


def to_rgb(img):
    img = ImageOps.exif_transpose(img)
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    if has_alpha:
        img = img.convert("RGBA")
        back = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(back, img)
    return img.convert("RGB")


def resize_long(img, long_side):
    w, h = img.size
    scale = long_side / max(w, h)
    size = (max(1, round(w * scale)), max(1, round(h * scale)))
    return img.resize(size, Image.Resampling.LANCZOS)


def render_pdf(data, dpi, page_no=0):
    doc = pymupdf.open(stream=data, filetype="pdf")
    index = min(page_no, len(doc) - 1)
    pix = doc[index].get_pixmap(dpi=dpi, alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def pdf_size(data, dpi):
    doc = pymupdf.open(stream=data, filetype="pdf")
    rect = doc[0].rect
    return round(rect.width / 72 * dpi), round(rect.height / 72 * dpi)


def image_size(data):
    with Image.open(io.BytesIO(data)) as img:
        img = ImageOps.exif_transpose(img)
        return img.size


def prepare(data, is_pdf, long_side, dpi):
    if is_pdf:
        img = render_pdf(data, dpi)
    else:
        img = to_rgb(Image.open(io.BytesIO(data)))
    img = resize_long(img, long_side)
    img.info = {}
    return img


def save_png(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", icc_profile=None)


def pixel_sha256(path):
    with Image.open(path) as img:
        rgb = img.convert("RGB")
        head = f"{rgb.width}x{rgb.height}".encode()
        return hashlib.sha256(head + rgb.tobytes()).hexdigest()


def png_chunks(path):
    names = []
    with open(path, "rb") as f:
        f.read(8)
        while True:
            head = f.read(8)
            if len(head) < 8:
                break
            length = int.from_bytes(head[:4], "big")
            names.append(head[4:8])
            f.seek(length + 4, 1)
    return names
