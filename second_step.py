import os

import telebot
from telebot import types
from dotenv import load_dotenv


def user_registration(token):
    bot = telebot.TeleBot(token, parse_mode=None)
    answers = []
    allergies = {"nuts": "Орехи", "lactose": "Лактоза"}
    subscription_periods = [1, 3, 6, 12]

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        markup = types.InlineKeyboardMarkup()
        start_subs = types.InlineKeyboardButton("Оформить подписку", callback_data='start_subs')
        markup.add(start_subs)
        bot.send_message(message.chat.id, "Для оформления подписки нажмите на кнопку", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def answer(call):
        markup = types.InlineKeyboardMarkup(row_width=4)
        if call.message:
            if call.data == "start_subs":
                bot.answer_callback_query(call.id)
                markup.add(
                    types.InlineKeyboardButton("Классическая", callback_data='classic_diet'),
                    types.InlineKeyboardButton("Вегетарианская", callback_data='vegan_diet'),
                    types.InlineKeyboardButton("Кето", callback_data='keto_diet')
                )
                bot.send_message(call.message.chat.id, "Выберите тип диеты:", reply_markup=markup)
                answers.append(call.data)
                print('Diet')
            if call.data == "classic_diet" or call.data == "vegan_diet" or call.data == "keto_diet":
                bot.answer_callback_query(call.id)
                markup.add(
                    types.InlineKeyboardButton("Один раз в день", callback_data='one_eat_time'),
                    types.InlineKeyboardButton("Два раза в день", callback_data='two_eat_time'),
                    types.InlineKeyboardButton("Три раза в день", callback_data='three_eat_time')
                )
                bot.send_message(call.message.chat.id, "Выберите количество приемов пищи:", reply_markup=markup)
                answers.append(call.data)
                print('Eat time')
            if call.data == "one_eat_time" or call.data == "two_eat_time" or call.data == "three_eat_time":
                bot.answer_callback_query(call.id)
                markup.add(
                    types.InlineKeyboardButton("1", callback_data='one_person'),
                    types.InlineKeyboardButton("2", callback_data='two_person'),
                    types.InlineKeyboardButton("3", callback_data='three_person'),
                    types.InlineKeyboardButton("4", callback_data='four_person')
                )
                bot.send_message(call.message.chat.id, "Выберите количество персон:", reply_markup=markup)
                answers.append(call.data)
                print('Person')
            if call.data == "one_person" or call.data == "two_person" or call.data == "three_person" or call.data == "four_person":
                bot.answer_callback_query(call.id)
                for allergy in allergies:
                    markup.add(
                        types.InlineKeyboardButton(allergies[allergy], callback_data=allergy)
                    )
                markup.add(
                    types.InlineKeyboardButton("У меня нет аллергии", callback_data="no_allergy")
                )
                bot.send_message(call.message.chat.id, "Есть ли у вас аллергия? На что?:", reply_markup=markup)
                answers.append(call.data)
                print('Allergy')
            if call.data in allergies or call.data == "no_allergy":
                bot.answer_callback_query(call.id)
                for period in subscription_periods:
                    markup.add(
                        types.InlineKeyboardButton(period, callback_data=period)
                    )
                bot.send_message(call.message.chat.id, "Выберите срок подписки (месяцев):", reply_markup=markup)
                answers.append(call.data)
                print('Period')
            if call.data in subscription_periods:
                print(answers)


    bot.infinity_polling()


if __name__ == '__main__':
    load_dotenv()

    tg_token = os.getenv('TELEGRAM_BOT_TOKEN')

    user_registration(tg_token)



