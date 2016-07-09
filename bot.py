# -*- coding: utf-8 -*-
# import os
# import time
import os.path
import random
import telebot
from telebot import types
from Source import utils, config
from Source.SQLighter import SQLighter
from Source.config import database_name


bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['game'])
def game(message):
    # Подключаемся к БД
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, database_name)
    db_worker = SQLighter(db_path)
    # Получаем случайную строку из БД
    row = db_worker.select_single(random.randint(1, utils.get_rows_count()))
    # Формируем разметку
    markup = utils.generate_markup(row[2], row[3])
    # Отправляем картинку с вариантами ответа
    bot.send_photo(message.chat.id, row[1], reply_markup=markup)
    # Включаем "игровой режим"
    utils.set_user_game(message.chat.id, row[2])
    # Отсоединяемся от БД
    db_worker.close()


@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
    # Если функция возвращает None -> Человек не в игре
    answer = utils.get_answer_for_user(message.chat.id)
    # Как Вы помните, answer может быть либо текст, либо None
    # Если None:
    if not answer:
        bot.send_message(message.chat.id, 'Чтобы начать игру, выберите команду /game')
    else:
        # Уберем клавиатуру с вариантами ответа.
        keyboard_hider = types.ReplyKeyboardHide()
        # Если ответ правильный/неправильный
        if message.text == answer:
            bot.send_message(message.chat.id, 'Верно!', reply_markup=keyboard_hider)
        else:
            bot.send_message(message.chat.id, 'Увы, Вы не угадали. Попробуйте ещё раз!', reply_markup=keyboard_hider)
        # Удаляем юзера из хранилища (игра закончена)
        utils.finish_user_game(message.chat.id)

    """
    # код для определения индентификатора картинки
@bot.message_handler(commands=['test'])
def find_file_ids(message):
    for file in os.listdir('stalkerMonster/'):
        if file.split('.')[-1] == 'jpg':
            f = open("stalkerMonster/"+file, 'rb')
            res = bot.send_voice(message.chat.id, f, None)
            print(res)
        time.sleep(3)
        """


if __name__ == '__main__':
    utils.count_rows()
    random.seed()
    bot.polling(none_stop=True)
