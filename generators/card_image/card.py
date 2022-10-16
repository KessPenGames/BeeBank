import base64
import random

import disnake
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling

abs_path = str(__file__).replace("card.py", "")

font_86 = ImageFont.truetype(f'{abs_path}/gothampro_medium.ttf', size=86)
font_36 = ImageFont.truetype(f'{abs_path}/gothampro_medium.ttf', size=36)

image_folder = f"{abs_path}/image/"
default_fons = [
    "black",
    "blue",
    "grey",
    "lime",
    "purple",
    "red",
    "yellow"
]
fons_format = ".png"


def bs64ToImg(bs64: str):
    with open(f"{abs_path}background.png", "wb") as f:
        f.write(base64.b64decode(bs64))
        f.close()


def generate(background: str, balance: str, name: str, card: int, color):
    bs64ToImg(background)
    img = Image.new('RGBA', (950, 595))

    back = Image.open(f"{abs_path}background.png").convert('RGBA')
    back = back.resize((950, 595), Resampling.LANCZOS)
    img.paste(back, (0, 0))

    draw = ImageDraw.Draw(img)

    draw.text((35, 40), "BEE", font=font_86, fill=color)
    draw.text((595, 500), str(card), font=font_86, fill=color)
    draw.text((35, 440), str(balance) + " АР", font=font_86, fill=color)

    draw.text((215, 78), "bank", font=font_36, fill=color)
    draw.text((40, 125), name, font=font_36, fill=color)

    remainder = f'{int(balance) // 64} ст. ' if int(balance) // 64 > 0 else ''
    draw.text((65, 515), f'{remainder}{int(balance) % 64} ар', font=font_36, fill=color)

    img.save(f'{abs_path}img.png')
    return disnake.File(f'{abs_path}img.png')


def random_img():
    with open(f'{image_folder}{random.choice(default_fons)}{fons_format}', "rb") as img_file:
        my_string = base64.b64encode(img_file.read())
    return my_string.decode('utf-8')
