import os

import telebot
from telebot import types
from dotenv import load_dotenv


def user_registration(token):
    bot = telebot.TeleBot(token, parse_mode=None)
    answers = []

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
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


    bot.infinity_polling()


if __name__ == '__main__':
    load_dotenv()

    tg_token = os.getenv('TELEGRAM_BOT_TOKEN')

    user_registration(tg_token)



