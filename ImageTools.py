from PIL import Image

def load_image(path):
    im = Image.open(path)
    return im

def merge(mode, channels):
    return Image.merge(mode, channels)

def prepare_image(path, pic):
    image = load_image(path)
    if image.mode == "RGBA" or image.mode == "L":
        image = image.convert("RGB")
    if image.mode == "P":
        image = image.convert(mode = "RGB", 
            palette = image.getpalette())
    return image

def get_data(original):
    data = original.convert("RGBA").tobytes("raw", "RGBA")
    return data

def apply_change(value):
    def change_pixels(x):
        x = x + value
        if x > 255:
            return 255
        elif x < 0:
            return 0
        else:
            return x
    return change_pixels

def change_color(pic, color, value):
    r, g, b = pic.original.split()
    if color == 'r':
        r = r.point(apply_change(value))
    if color == 'g':
        g = g.point(apply_change(value))
    if color == 'b':
        b = b.point(apply_change(value))
    return merge("RGB", (r, g, b))