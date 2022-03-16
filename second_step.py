import os

import telebot
from telebot import types
from dotenv import load_dotenv


def user_registration(token):
    bot = telebot.TeleBot(token, parse_mode=None)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("Оформить подписку", url='https://test.test')
        markup.add(button1)
        bot.send_message(message.chat.id, "Для оформления подписки нажмите на кнопку", reply_markup=markup)

    bot.infinity_polling()


if __name__ == '__main__':
    load_dotenv()

    tg_token = os.getenv('TELEGRAM_BOT_TOKEN')

    user_registration(tg_token)



