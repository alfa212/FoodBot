import json
import os
from random import choice

import telebot
from telebot import types
from dotenv import load_dotenv

import keyboard as kb
from recipes_parser import main as parser


def get_user_info(user_id):
    with open('users.json', 'r', encoding='utf-8') as json_file:
        users = json.load(json_file)
    if user_id in users:
        user = users[user_id]
        first_name = user['name']
        last_name = user['last_name']
        subscription = user['subscriptions']
        return first_name, last_name, subscription


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


def user_payment(token, pay_token, admin_id):
    bot = telebot.TeleBot(token, parse_mode=None)

    prices = [
        types.LabeledPrice(label='Подписка на 1 месяц', amount=10000),
        types.LabeledPrice(label='Подписка на 3 месяца', amount=30000),
        types.LabeledPrice(label='Подписка на 6 месяцев', amount=60000),
        types.LabeledPrice(label='Подписка на 1 год', amount=120000),
    ]

    @bot.message_handler(commands=['start'])
    def start(message):
        bot.send_message(message.chat.id, 'Привет', reply_markup=kb.markup_kb_full)


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
    def get_payment(message):
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
        user_id = str(message.from_user.id)
        if get_user_info(user_id):
            first_name, last_name, subscriptions = get_user_info(user_id)
            bot.send_message(
                message.chat.id,
                f'<b>{first_name} {last_name}</b>, Добро пожаловать в личный кабинет!',
                parse_mode='HTML',
                reply_markup=kb.inline_kb_full
            )
        else:
            bot.send_message(
                message.chat.id,
                'Вы не являетесь зарегистрированным пользователем. Пожалуйста пройдите регистраци!'
            )

    @bot.callback_query_handler(func=lambda call: True)
    def process_check_btn(callback_query):
        answer = callback_query.data
        chat_id = callback_query.message.chat.id
        user_id = str(callback_query.from_user.id)
        first_name, last_name, subscriptions = get_user_info(user_id)
        title, ingredients, recipe_steps, image_path = get_recipe_info()
        if answer == 'subscription':
            if len(subscriptions) > 0:
                bot.answer_callback_query(callback_query.id)
                bot.send_message(chat_id, 'Подписка оформлена', reply_markup=kb.inline_kb_full)
            else:
                bot.answer_callback_query(callback_query.id)
                bot.send_message(chat_id, 'Подписка не оформлена', reply_markup=kb.inline_kb_full)

        elif answer == 'recipe':
            with open(image_path, 'rb') as file:
                image = file.read()
            bot.answer_callback_query(callback_query.id)
            bot.send_photo(
                chat_id=chat_id,
                photo=image,
                caption=f'<b>{title}</b>\n\n{ingredients}\n\n{recipe_steps}',
                parse_mode='HTML',
                reply_markup=kb.inline_kb_full
            )

        elif answer == 'shopping_list':
            bot.answer_callback_query(callback_query.id)
            bot.send_message(chat_id, ingredients, reply_markup=kb.inline_kb_full)

    @bot.message_handler(commands=['parse'])
    def parse_recipe(message):
        user = message.from_user.id
        if user == int(admin_id):
            parser()
            bot.send_message(
                message.chat.id,
                'Рецепты добавлены в базу данных'
            )
        else:
            bot.send_message(
                message.chat.id,
                'Данная функция доступна только для администратора'
            )


    bot.infinity_polling(skip_pending=True)


def main():
    load_dotenv()

    tg_token = os.getenv('BOT_TOKEN')
    pay_token = os.getenv('PAY_TOKEN')
    admin_id = os.getenv('ADMIN_ID')

    user_payment(tg_token, pay_token, admin_id)


if __name__ == '__main__':
    main()
