import os
import random
import textwrap

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont


def add_text(name):
    load_dotenv()
    path_img = os.getenv('path_img')
    path_collection = os.getenv('path_collection')

    try:
        photo = Image.open(os.path.join(path_img, name))
    except Exception as e:
        print('При загрузке фотографии возникла ошибка: {}'.format(e))

    idraw = ImageDraw.Draw(photo)
    width, height = photo.size

    # открыть сборник и выбрать рандомную подпись из списка
    with open(path_collection, 'r') as file:
        words_list = file.readlines()
        text = words_list[random.randint(0, len(words_list) - 1)]

    font = ImageFont.truetype('Lobster.ttf', size=75)

    # установить максимально возможную ширину подписи
    # и построчно разместить текст на фото
    lines = textwrap.wrap(text, width=15)
    for line in lines:
        w, h = font.getsize(line)
        idraw.text((
            (width - w) / 2, height - 350
            ), line, font=font, stroke_width=2, stroke_fill='black')
        height += h

    photo.save(os.path.join(path_img, name))
