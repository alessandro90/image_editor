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

def change_pixel_color(value):
    def apply(x):
        return x + value
    return apply

def change_color(pic, color, directional_slider):
    r, g, b = pic.original.split()
    modes = {'r' : r, 'g' : g, 'b' : b}
    direction = directional_slider.direction
    previous_val = directional_slider.previous_val
    current_val = directional_slider.value()
    if direction != 0:
        val = direction * abs(current_val - previous_val)
        modes[color] = modes[color].point(change_pixel_color(val))
        directional_slider.previous_val = current_val
    return merge("RGB", list(modes.values()))
