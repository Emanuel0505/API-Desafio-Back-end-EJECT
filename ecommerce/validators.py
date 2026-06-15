import re

def invalid_color_hexadecimal(color):
    """Return True when the color value is not a valid 3 or 6 digit hex code."""
    model = r'^#?([0-9A-F]{6}|[0-9A-F]{3})$'
    response = re.findall(model,color)
    return not response
