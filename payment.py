import json
import os
from random import choice

import telebot
from telebot import types
from dotenv import load_dotenv

import keyboard as kb


def get_recipe_info():
    with open('recipes.json', 'r', encoding='utf-8') as json_file:
        recipes = json.load(json_file)
    rand_recipe_num = choice(list(recipes))

    recipe = recipes[rand_recipe_num]

    title = recipe['title']
    ingredients = '\n'.join(recipe['ingredients'])
    recipe_steps = '\n'.join(recipe['recipe_steps'])
    image_path = recipe['image_path']

    return title, ingredients, recipe_steps, image_path


def user_payment(token, pay_token):
    bot = telebot.TeleBot(token, parse_mode=None)

    prices = [
        types.LabeledPrice(label='Подписка на 1 месяц', amount=10000),
        types.LabeledPrice(label='Подписка на 3 месяца', amount=30000),
        types.LabeledPrice(label='Подписка на 6 месяцев', amount=60000),
        types.LabeledPrice(label='Подписка на 1 год', amount=120000),
    ]

    @bot.message_handler(commands=['buy'])
    def process_buy_command(message):
        bot.send_message(message.chat.id, 'Проверка тестовых платежей')
        for price in prices:
            bot.send_invoice(
                message.chat.id,
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
                          'попробуйте оплатить через пару минут.'
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
        # message_id = callback_query.message.id
        title, ingredients, recipe_steps, image_path = get_recipe_info()
        if answer == 'subscription':
            bot.answer_callback_query(callback_query.id)
            bot.send_message(chat_id, 'Подписка оформлена', reply_markup=kb.inline_kb_full)

        elif answer == 'recipe':
            with open(image_path, 'rb') as file:
                image = file.read()
            bot.answer_callback_query(callback_query.id)
            bot.send_message(chat_id, f'<b>{title}</b>', parse_mode='HTML')
            bot.send_photo(chat_id, image)
            bot.send_message(chat_id, ingredients)
            bot.send_message(chat_id, recipe_steps, reply_markup=kb.inline_kb_full)

        elif answer == 'shopping_list':
            bot.answer_callback_query(callback_query.id)
            bot.send_message(chat_id, ingredients, reply_markup=kb.inline_kb_full)

    bot.infinity_polling(skip_pending=True)


def main():
    load_dotenv()

    tg_token = os.getenv('BOT_TOKEN')
    pay_token = os.getenv('PAY_TOKEN')

    user_payment(tg_token, pay_token)


if __name__ == '__main__':
    main()
