import json
import os

import telebot
from telebot import types
from dotenv import load_dotenv


def user_registration(token, users):
    bot = telebot.TeleBot(token, parse_mode=None)
    answers = []

    class User:
        def __init__(self, first_name, last_name=None, phone=None):
            self.first_name = first_name
            self.last_name = last_name
            self.phone = phone

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name if message.from_user.last_name else ''
        full_name = f'{first_name} {last_name}'
        msg = bot.reply_to(
            message, f'Добрый день, {full_name}!\n'
        )
        # markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup = types.InlineKeyboardMarkup()
        user_name = types.InlineKeyboardButton(f'{full_name}', callback_data='user_name')
        custom_name = types.InlineKeyboardButton('Другое имя', callback_data='custom_name')
        markup.add(user_name, custom_name)
        # name_choice = bot.reply_to(msg, 'Могу я дальше вас так называть или хотите ввести другое имя?', reply_markup=markup)
        bot.reply_to(msg, 'Могу я дальше вас так называть или хотите ввести другое имя?',
                                   reply_markup=markup)
    def write_new_name_step(message):
        message = bot.reply_to(message, 'Введите имя: ')
        bot.register_next_step_handler(message, process_name_step)

    def process_name_step(message):
        try:
            if message.data == 'user_name':
                pass  # TODO
            users[f'{message.from_user.id}'] = {}  # User(name)
            users[f'{message.from_user.id}']['name'] = message.text
            msg = bot.reply_to(message, 'Введите ваш номер телефона: ')
            bot.register_next_step_handler(msg, process_phone_step)
        except Exception as e:
            print(e)
            bot.reply_to(message, 'Произошла ошибка, попробуйте зарегистрироваться заново, отправив "/start"')

    def process_phone_step(message):
        try:
            phone_number = message.text
            users[f'{message.from_user.id}']['phone_number'] = phone_number
            bot.send_message(message.chat.id, str(users[f'{message.from_user.id}']))
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Оформить подписку')
            msg = bot.reply_to(message, 'Оформите подписку', reply_markup = markup)
            bot.register_next_step_handler(msg, subscribe_step)
        except Exception as e:
            bot.reply_to(message, 'Произошла ошибка, попробуйте зарегистрироваться заново, отправив "/start"')

    def subscribe_step(message):
        markup = types.InlineKeyboardMarkup()
        start_subs = types.InlineKeyboardButton("Оформить подписку", callback_data='start_subs')
        markup.add(start_subs)
        bot.send_message(message.chat.id, "Для оформления подписки нажмите на кнопку", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def answer(call):
        markup = types.InlineKeyboardMarkup()
        if call.message:
            if call.data == "start_subs":
                bot.answer_callback_query(call.id)
                classic_diet = types.InlineKeyboardButton("Классическая", callback_data='classic_diet')
                vegan_diet = types.InlineKeyboardButton("Вегетарианская", callback_data='vegan_diet')
                keto_diet = types.InlineKeyboardButton("Кето", callback_data='keto_diet')
                markup.add(classic_diet, vegan_diet, keto_diet)
                bot.send_message(call.message.chat.id, "Выберите тип диеты:", reply_markup=markup)
                answers.append(call.data)
                print(call.data)
            if call.data == "classic_diet" or call.data == "vegan_diet" or call.data == "keto_diet":
                bot.answer_callback_query(call.id)
                one_eat_time = types.InlineKeyboardButton("Один раз в день", callback_data='one_eat_time')
                two_eat_time = types.InlineKeyboardButton("Два раза в день", callback_data='two_eat_time')
                three_eat_time = types.InlineKeyboardButton("Три раза в день", callback_data='three_eat_time')
                markup.add(one_eat_time, two_eat_time, three_eat_time)
                bot.send_message(call.message.chat.id, "Выберите количество приемов пищи:", reply_markup=markup)
                answers.append(call.data)
                print(call.data)
            if call.data == 'custom_name':
                message = bot.reply_to(call.message, 'Введите имя: ')
                bot.register_next_step_handler(message, write_new_name_step)
            if call.data == 'user_name':
                bot.register_next_step_handler(call.message, process_name_step)


    bot.infinity_polling()


if __name__ == '__main__':
    load_dotenv()

    tg_token = os.getenv('TELEGRAM_BOT_TOKEN')

    try:
        with open('users.json', mode='r', encoding='utf-8') as file:
            users = json.loads(file.read())
    except FileNotFoundError:
        users = {}

    user_registration(tg_token, users)



