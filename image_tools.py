from PIL import Image
from PIL import ImageChops
from PIL import ImageEnhance

def load_image(path):
    im = Image.open(path)
    return im

def merge(channels, mode = "RGB"):
    return Image.merge(mode, channels)

def copy(pic):
    return pic.copy()

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

def change_pixel_color(value):
    def apply(x):
        return x + value
    return apply

def equal(im1, im2):
    return ImageChops.difference(im1, im2).getbbox() is None

def get_cache_colors(pic):
    return pic.original.split()

def change_color(pic, color, slider):
    r, g, b = pic.original.split()
    dr, dg, db = pic.to_display.split()
    colors = 'red', 'green', 'blue'
    modes = {'red' : r, 'green' : g, 'blue' : b}
    dmodes = {'red' : dr, 'green' : dg, 'blue' : db}
    m = {}
    if all([equal(modes[i], dmodes[i]) for i in colors if i != color]):
        m = modes
    else:
        m[color] = modes[color]
        for i in colors:
            if i != color:
                m[i] = dmodes[i]
    m[color] = m[color].point(change_pixel_color(slider.value()))
    cache_colors = (m[colors[0]], m[colors[1]], m[colors[2]])
    return merge(cache_colors), cache_colors

def change_color_balance(pic, slider):
    if pic.changed_contrast:
        pic.cache_colors = copy(pic.to_display).split()
        pic.changed_contrast = False
    image = merge(pic.cache_colors)
    enh = ImageEnhance.Color(image)
    enhanced_pic = enh.enhance(slider.value())
    pic.changed_color_balance = True
    return enhanced_pic

def change_contrast(pic, slider):
    if pic.changed_color_balance:
        pic.cache_colors = copy(pic.to_display).split()
        pic.changed_color_balance = False
    image = merge(pic.cache_colors)
    enh = ImageEnhance.Contrast(image)
    enhanced_pic = enh.enhance(slider.value())
    pic.changed_contrast = True
    return enhanced_pic
