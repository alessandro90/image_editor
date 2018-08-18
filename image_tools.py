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

def build_effects_dict(func):
    func.effects = {'Color' : 'changed_color_balance',
                    'Brightness' : 'changed_brightness',
                    'Contrast' : 'changed_contrast',
                    'Sharpness' : 'changed_sharpness'}
    return func

@build_effects_dict
def change_effect(pic, slider, effect):
    check_effects = {}
    for k, v in change_effect.effects.items():
        if k != effect:
            check_effects[v] = getattr(pic, v)
    if any(check_effects.values()):
        pic.cache_colors = pic.to_display.split()
        for attr in check_effects.keys():
            setattr(pic, attr, False)
    image = merge(pic.cache_colors)
    setattr(pic, change_effect.effects[effect], True)
    enh = getattr(ImageEnhance, effect)(image)
    return enh.enhance(slider.value())