import os

import telebot
from telebot import types
from dotenv import load_dotenv

import keyboard as kb


def user_registration(token, pay_token):
    bot = telebot.TeleBot(token, parse_mode=None)
    answers = []
    allergies_answers = []
    allergies = {"nuts": "Орехи", "lactose": "Лактоза"}
    subscription_periods = ["1", "3", "6", "12"]
    one_meal_cost = 1

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
                    types.InlineKeyboardButton("Отлично! Оформляем!", callback_data="/buy")
                )
                bot.send_message(call.message.chat.id, f"Стоимость вашей подписки составит: {total_price} руб.", reply_markup=markup)
                answers.append(total_price)
                print(answers)
            if call.data == "/buy":
                print('нажал подписку')
                bot.answer_callback_query(call.id)
                bot.send_message(call.message.chat.id, 'Проверка тестовых платежей')
                price = types.LabeledPrice(label='Подписка на 1 месяц', amount=answers[-1]*100)
                print(answers[-1])
                bot.send_invoice(
                    call.message.chat.id,
                    title=price.label,
                    description='Тестовый платеж',
                    provider_token=pay_token,
                    currency='rub',
                    prices=[price],
                    start_parameter='subsription-example',
                    invoice_payload='some-invoice-payload-for-our-internal-use'
                )

                @bot.pre_checkout_query_handler(func=lambda query: True)
                def checkout(pre_checkout_query):
                    bot.answer_pre_checkout_query(
                        pre_checkout_query.id,
                        ok=True,
                        error_message='Инопланетяне пытались угнать ваш CVV, но мы защитили ваши данные, '
                                      'поппробуйте оплатить через пару минут.'
                    )


                @bot.message_handler(content_types=['successful_payment'])
                def got_payment(message):
                    pay_message = f'Спасибо за оплату! Вы оплатили ' \
                                  f'{message.successful_payment.total_amount / 100} ' \
                                  f'{message.successful_payment.currency} ' \
                                  f'за подписку на индивидуальное меню'

                    print('successful_payment:')
                    print(f'От пользователя: {message.from_user.id} '
                          f'поступил платеж с id: {message.successful_payment.telegram_payment_charge_id} '
                          f'в размере: {message.successful_payment.total_amount / 100} {message.successful_payment.currency}')

                    bot.send_message(
                        message.chat.id,
                        pay_message,
                        parse_mode='Markdown'
                    )


                @bot.message_handler(commands=['account'])
                def account(message):
                    bot.send_message(
                        message.chat.id,
                        'Добро пожаловать в личный кабинет'
                    )
                    bot.send_message(
                        message.chat.id,
                        "Для проверки статуса подписки нажмите на кнопку",
                        reply_markup=kb.inline_kb_full
                    )


                @bot.callback_query_handler(func=lambda call: True)
                def process_check_btn(callback_query):
                    answer = callback_query.data
                    chat_id = callback_query.message.chat.id
                    message_id = callback_query.message.id

                    if answer == 'check_subs':
                        bot.answer_callback_query(callback_query.id)
                        bot.edit_message_text(
                            'Подписка оформлена',
                            chat_id=chat_id,
                            message_id=message_id,
                            reply_markup=kb.inline_kb_full
                        )

                    # elif answer == 'get_recipe':
                    #     recipe_html = get_recipe_info()
                    #     bot.answer_callback_query(callback_query.id)
                    #     bot.send_message(chat_id, recipe_html, parse_mode='HTML', reply_markup=kb.inline_kb_full)
                    #     bot.edit_message_text(
                    #         recipe_html,
                    #         chat_id=chat_id,
                    #         message_id=message_id,
                    #         reply_markup=kb.inline_kb_full,
                    #         parse_mode='HTML'
                    #     )

                    elif answer == 'get_shopping_list':
                        bot.answer_callback_query(callback_query.id)
                        bot.edit_message_text(
                            'Список покупок',
                            chat_id=chat_id,
                            message_id=message_id,
                            reply_markup=kb.inline_kb_full
                        )

    bot.infinity_polling()


if __name__ == '__main__':
    load_dotenv()

    tg_token = os.getenv('TELEGRAM_BOT_TOKEN')
    pay_token = os.getenv('PAY_TOKEN')

    user_registration(tg_token, pay_token)



