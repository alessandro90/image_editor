from PIL import Image,        \
                ImageChops,   \
                ImageEnhance, \
                ImageFilter

def load_image(path):
    im = Image.open(path)
    return im

def merge(channels, mode = "RGBA"):
    return Image.merge(mode, channels)

def prepare_image(path, pic):
    image = load_image(path)
    if image.mode == "L" or image.mode == 'RGB':
        image = image.convert("RGBA")
    if image.mode == "P":
        image = image.convert(mode = "RGBA", 
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

def get_modes(pic):
    return pic.split()

def change_RGB_color(pic, color, slider):
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
    return pic.to_display.filter(getattr(ImageFilter, name))

def make_transparent(pic):
    data = pic.to_display.getdata()
    trsp_image_data = []
    for pix in data:
        if pix[:3] == (255, 255, 255):
            trsp_image_data.append((255, 255, 255, 0))
        else:
            trsp_image_data.append(pix)
    # Because of this line, pic.original must always be
    # copied, otherwise putdata will modify also pic.original
    # since pic.to_display would point to pic.original.
    pic.to_display.putdata(trsp_image_data)

def set_alpha(dest, source):
    dest.putalpha(source)
