"""
This module contains all the PIL-related functions.
Only in this module there are imports from the PIL library.
"""

from PIL import Image,        \
                ImageChops,   \
                ImageEnhance, \
                ImageFilter
def load_image(path):
    """
    Load selected image.
    """
    im = Image.open(path)
    return im

def merge(channels, mode = "RGBA"):
    """
    Shortcut for Image.merge.
    """
    return Image.merge(mode, channels)

def prepare_image(path, pic):
    """
    Convert loaded image to RGBA format.
    """
    image = load_image(path)
    if image.mode == "L" or image.mode == 'RGB':
        image = image.convert("RGBA")
    if image.mode == "P":
        image = image.convert(mode = "RGBA", 
            palette = image.getpalette())
    return image

def get_data(original):
    """
    Get the image as a bytes object.
    """
    data = original.tobytes("raw", "RGBA")
    return data

def change_pixel_color(value):
    """
    Increase color channel by a fixed value.
    """
    def apply(x):
        return x + value
    return apply

def equal(im1, im2):
    """
    Returns whether two images are equal.
    """
    return ImageChops.difference(im1, im2).getbbox() is None

def get_modes(pic):
    """
    Shortcut for Image.split.
    """
    return pic.split()

def change_RGB_color(pic, color, slider):
    """
    Increase the value of the channel 'color' of the displayed
    image by an amount equal to 'slider.value()'.
    """
    r, g, b, _ = get_modes(pic.original)
    dr, dg, db, alpha = get_modes(pic.to_display)
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
    cache_colors = (m[colors[0]], m[colors[1]], m[colors[2]], alpha)
    return merge(cache_colors)

def change_effect(pic, slider, effect, effects):
    """
    Apply an effect to the displayed image.
    """
    check_effects = {}
    for k, v in effects.items():
        if k != effect:
            check_effects[k] = v
    if any(check_effects.values()):
        pic.cache_colors = get_modes(pic.to_display)
        for attr in check_effects.keys():
            effects[attr] = False
    image = merge(pic.cache_colors)
    effects[effect] = True
    enh = getattr(ImageEnhance, effect)(image)
    return enh.enhance(slider.value())

def apply_filter(pic, name):
    """
    Apply a predefined filter to the displayed image.
    """
    return pic.to_display.filter(getattr(ImageFilter, name))

def make_transparent(pic):
    """
    Make all white pixels transparent.
    """
    data = pic.to_display.getdata()
    trsp_image_data = []
    for pix in data:
        if pix[:3] == (255, 255, 255):
            trsp_image_data.append((255, 255, 255, 0))
        else:
            trsp_image_data.append(pix)
    pic.white_pixels = white_pixels(data)
    # Because of this line, pic.original must always be
    # copied, otherwise putdata will modify also pic.original
    # since pic.to_display would point to pic.original.
    pic.to_display.putdata(trsp_image_data)

def white_pixels(data):
    """
    Generator which returns all the white pixels positions
    before the 'make_transparent' call.
    """
    for index, pix in enumerate(data):
        if pix[:3] == (255, 255, 255):
            yield index

def reset_alpha(pic):
    """
    Restore the original white pixels before the call 
    to 'make_transparent'.
    """
    if pic.white_pixels:
        data = list(pic.to_display.getdata())
        for i in pic.white_pixels:
            data[i] = (255, 255, 255, 0)
        pic.to_display.putdata(data)
        pic.to_display.putalpha(pic.original_alpha)
