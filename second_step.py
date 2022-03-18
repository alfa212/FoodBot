import os

import telebot
from telebot import types
from dotenv import load_dotenv


def user_registration(token):
    bot = telebot.TeleBot(token, parse_mode=None)
    answers = []
    allergies_answers = []
    allergies = {"nuts": "Орехи", "lactose": "Лактоза"}
    subscription_periods = ["1", "3", "6", "12"]
    one_meal_cost = 100

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        markup = types.InlineKeyboardMarkup()
        start_subs = types.InlineKeyboardButton("Оформить подписку", callback_data='start_subs')
        markup.add(start_subs)
        bot.send_message(message.chat.id, "Для оформления подписки нажмите на кнопку", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def answer(call):
        markup = types.InlineKeyboardMarkup(row_width=1)
        if call.message:
            if call.data == "start_subs":
                bot.answer_callback_query(call.id)
                markup.add(
                    types.InlineKeyboardButton("Классическая", callback_data='classic_diet'),
                    types.InlineKeyboardButton("Вегетарианская", callback_data='vegan_diet'),
                    types.InlineKeyboardButton("Кето", callback_data='keto_diet')
                )
                bot.send_message(call.message.chat.id, "Выберите тип диеты:", reply_markup=markup)
                print('Diet')
            if call.data == "classic_diet" or call.data == "vegan_diet" or call.data == "keto_diet":
                bot.answer_callback_query(call.id)
                markup.add(
                    types.InlineKeyboardButton("Один раз в день", callback_data='1_eat_time'),
                    types.InlineKeyboardButton("Два раза в день", callback_data='2_eat_time'),
                    types.InlineKeyboardButton("Три раза в день", callback_data='3_eat_time')
                )
                bot.send_message(call.message.chat.id, "Выберите количество приемов пищи:", reply_markup=markup)
                answers.append(call.data)
                print('Eat time')
            if call.data == "1_eat_time" or call.data == "2_eat_time" or call.data == "3_eat_time":
                bot.answer_callback_query(call.id)
                markup.add(
                    types.InlineKeyboardButton("1", callback_data='1_person'),
                    types.InlineKeyboardButton("2", callback_data='2_person'),
                    types.InlineKeyboardButton("3", callback_data='3_person'),
                    types.InlineKeyboardButton("4", callback_data='4_person')
                )
                bot.send_message(call.message.chat.id, "Выберите количество персон:", reply_markup=markup)
                answers.append(call.data)
                print('Person')
            if call.data == "1_person" or call.data == "2_person" or call.data == "3_person" or call.data == "4_person":
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
            if call.data in allergies:
                bot.answer_callback_query(call.id)
                for allergy in allergies:
                    if allergy == call.data or allergy in allergies_answers:
                        markup.add(
                            types.InlineKeyboardButton(f"{allergies[allergy]} ✅", callback_data=allergy)
                        )
                    else:
                        markup.add(
                            types.InlineKeyboardButton(allergies[allergy], callback_data=allergy)
                        )
                markup.add(
                    types.InlineKeyboardButton("Подтвердить выбор", callback_data="end_allergy")
                )
                bot.edit_message_text(chat_id=call.message.chat.id, text="Есть ли у вас аллергия? На что?",
                                      message_id=call.message.message_id, reply_markup=markup)
                allergies_answers.append(call.data)
                print('Выбор')
                allergies_answers.append(call.data)
                answers.append(call.data)
            if call.data == "no_allergy" or call.data == "end_allergy":
                bot.answer_callback_query(call.id)
                for period in subscription_periods:
                    markup.add(
                        types.InlineKeyboardButton(period, callback_data=period)
                    )
                bot.send_message(call.message.chat.id, "Выберите срок подписки (месяцев):", reply_markup=markup)
                # answers.append(allergies_answers)
                allergies_answers.clear()
                print('Period')
            if call.data in subscription_periods:
                bot.answer_callback_query(call.id)
                total_price = round(one_meal_cost * int(answers[1][0]) * int(answers[2][0]) * 30 * int(call.data) * (int(call.data) * 1 / (int(call.data) * 1.67)))
                markup.add(
                    types.InlineKeyboardButton("Отлично! Оформляем!", callback_data="i_agree")
                )
                bot.send_message(call.message.chat.id, f"Стоимость вашей подписки составит: {total_price} руб.", reply_markup=markup)
                print(answers)
                answers.clear()
                # print(one_meal_cost)
                # print(int(answers[2][0]))
                # print(int(answers[3][0]))
                # print(int(call.data))


    bot.infinity_polling()


if __name__ == '__main__':
    load_dotenv()

    tg_token = os.getenv('TELEGRAM_BOT_TOKEN')

    user_registration(tg_token)



