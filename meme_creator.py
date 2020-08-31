#!/usr/bin/env python3
import os
import random
import textwrap
import time
from datetime import datetime

import pytz
import requests
import telebot
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from telebot import types


def main():
    # импорт настроек из виртуального окружения
    load_dotenv()
    token = os.getenv('telegram_token')
    path_img = os.getenv('path_img')
    path_collection = os.getenv('path_collection')

    bot = telebot.TeleBot(token, parse_mode='html')
    
    # функция, которая добавляет подпись к фото
    def add_text(name):
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

    # Приветственое сообщение от бота
    @bot.message_handler(commands=['start'])
    def start(message):
        text = f'<b>Привет, {message.from_user.first_name}! 🙂</b> \
            \nСкидывай фото и я пришлю мем в ответ!'
        bot.send_message(message.chat.id, text)

    @bot.message_handler(content_types=['photo'])
    def create_meme(message):
        try:
            # после получения фото определяем id пользователя
            # и дату отправки фото для указания в имени файла
            user_id = message.from_user.id
            timestamp = message.date
            date = datetime.fromtimestamp(
                timestamp, pytz.timezone('Europe/Moscow')
                ).strftime('%Y-%m-%d_%H:%M')

            name = '{}_{}.jpg'.format(date, str(user_id))

            # направляем http-запрос на сервер Телеграм,
            # получаем фото и сохраняем его
            file_info = bot.get_file(message.photo[-1].file_id)
            file = requests.get(
                'https://api.telegram.org/file/bot{0}/{1}'.format(
                    token, file_info.file_path
                )
            )
            with open(os.path.join(path_img, name), 'wb') as new_file:
                new_file.write(file.content)
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, 'Что-то пошло не так...😟')
    
        # добавляем подпись к фото
        add_text(name)

        try:
            bot.send_message(
                message.chat.id, '<b>Процесс создания мема запущен...⚙️</b>'
            )
            time.sleep(2)
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, 'Что-то пошло не так...😟')

        # отправляем пользователю готовый мем и предлагаем сделать репост
        try:
            with open(os.path.join(path_img, name), 'rb') as photo:
                keyboard = types.InlineKeyboardMarkup()
                callback_button = types.InlineKeyboardButton(
                    'Сделать репост', callback_data="Репост"
                )
                keyboard.add(callback_button)
                bot.send_photo(message.chat.id, photo, reply_markup=keyboard)
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, 'Что-то пошло не так...😟')

    # Обработчик обратного вызова: если пользователь нажал "Сделать репост",
    # уведомляем, что мем попадет в общий чат и ждем решения (Да/Нет)
    @bot.callback_query_handler(func=lambda call: call.data == 'Репост')
    def callback_repost(call):
        try:
            if call.data == 'Репост':
                keyboard = types.InlineKeyboardMarkup()
                yes_btn = types.InlineKeyboardButton('Да', callback_data="Да")
                no_btn = types.InlineKeyboardButton('Нет', callback_data="Нет")
                keyboard.add(yes_btn, no_btn)
                bot.reply_to(
                    call.message,
                    'Отправить мем в канал @memes_chat?',
                    reply_markup=keyboard
                )
                bot.answer_callback_query(call.id, text="")
        except Exception as e:
            print(e)
            bot.send_message(call.from_user.id, 'Что-то пошло не так...😟')

    # Обработчик обратного вызова:
    # если пользователь нажал "Да" - скидываем мем в общий чат
    @bot.callback_query_handler(func=lambda call: call.data == 'Да')
    def callback_yes(call):
        try:
            bot.send_photo(
                '@memes_chat',
                call.message.reply_to_message.json['photo'][-1]['file_id']
            )
            time.sleep(2)
            bot.send_message(
                call.from_user.id,
                'Готово! Скидывай фото и я сделаю новый мем!'
            )
            bot.answer_callback_query(call.id, text="")
        except Exception as e:
            print(e)
            bot.send_message(call.from_user.id, 'Что-то пошло не так...😟')

    # Обработчик обратного вызова:
    # если пользователь нажал "Нет" - предлагаем сделать еще один мем
    @bot.callback_query_handler(func=lambda call: call.data == 'Нет')
    def callback_no(call):
        try:
            bot.send_message(
                call.from_user.id,
                'Скидывай фотo - я пришлю другой мем!'
            )
            bot.answer_callback_query(call.id, text="")
        except Exception as e:
            print(e)
            bot.send_message(call.from_user.id, 'Что-то пошло не так...😟')

    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
