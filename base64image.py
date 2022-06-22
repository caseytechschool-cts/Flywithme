from os import path
import base64

"""A simple function for converting the source image into a base64 data for universal use.
:param name: (str) the name of the image file
:return: the base64 of the image file
"""


def image_to_base64(name):
    with open(path.join("images", name), "rb") as data:
        image_data = data.read()
        return base64.b64encode(image_data)