from PIL import Image

def load_image(path):
    im = Image.open(path)
    return im

def prepare_image(path, pic):
    image = load_image(path)
    if image.mode == "RGBA" or image.mode == "L":
        image = image.convert("RGB")
    if image.mode == "P":
        image = image.convert(mode = "RGB", 
            palette = image.getpalette())
    # This is the only way to avoid a Windows crash.
    r, g, b = image.split()
    image = Image.merge("RGB", (b, g, r))
    return image

def get_data(original):
    data = original.convert("RGBA").tobytes("raw", "RGBA")
    return data