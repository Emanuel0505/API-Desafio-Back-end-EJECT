import re

def invalid_color_hexadecimal(color):
    model = r'^#?([0-9A-F]{6}|[0-9A-F]{3})$'
    response = re.findall(model,color)
    return not response
