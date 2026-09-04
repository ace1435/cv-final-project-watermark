import io

import fitz
from PIL import Image

from wmbench.prep import image_size, pdf_size, png_chunks, png_meta_chunks, prepare, save_png


def jpeg_with_orientation(size, orientation):
    img = Image.new("RGB", size, (200, 30, 30))
    exif = Image.Exif()
    exif[274] = orientation
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif.tobytes())
    return buf.getvalue()


def png_with_gamma(size):
    img = Image.new("RGBA", size, (0, 0, 255, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG", gamma=0.45455)
    return buf.getvalue()


def pdf_bytes():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((72, 72), "hello")
    return doc.tobytes()


def test_exif_orientation_applied():
    data = jpeg_with_orientation((3000, 2000), 6)
    assert image_size(data) == (2000, 3000)
    img = prepare(data, False, 1024, 150)
    assert img.size == (683, 1024)


def test_alpha_composited_on_white_and_chunks_stripped(tmp_path):
    img = prepare(png_with_gamma((2048, 1024)), False, 1024, 150)
    assert img.size == (1024, 512)
    assert img.getpixel((0, 0)) == (255, 255, 255)
    out = tmp_path / "x.png"
    save_png(img, out)
    chunks = png_chunks(out)
    assert chunks[0] == b"IHDR"
    assert chunks[-1] == b"IEND"
    assert not any(c in png_meta_chunks for c in chunks)


def test_pdf_render_size():
    data = pdf_bytes()
    assert pdf_size(data, 150) == (1240, 1754)
    img = prepare(data, True, 1024, 150)
    assert img.size == (724, 1024)
    assert img.mode == "RGB"
