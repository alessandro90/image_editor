from PIL import Image

def prepare_image(path, pic):
    im = Image.open(path)
    original = im.copy()
    # Check bands
    if im.mode == "RGBA" or im.mode == "L":
        im = im.convert("RGB")
    if im.mode == "P":
        im = im.convert(mode = "RGB", palette = im.getpalette())
    # This is the only way to avoid a Windows crash.
    r, g, b = im.split()
    im = Image.merge("RGB", (b, g, r))
    data = im.convert("RGBA").tobytes("raw", "RGBA")
    return im, data, original