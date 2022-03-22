import os
import json
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

def add_new_user(user_id, name, last_name, phone_num, subscription, diet, meals_number, persons_number, allergies):
    try:
        with open('users.json', 'r', encoding='utf-8') as json_file:
            users = json.load(json_file)
    except:
        users = {}

    users[user_id] = {
        "name": name,
        "last_name": last_name,
        "phone_number": phone_num,
        "subscriptions": [],
        "diet": diet,
        "meals_number": meals_number,
        "persons_number": persons_number,
        "allergies": allergies,
        "favourite_dishes": [],
        "disliked_dishes": []
    }
    users[user_id]["subscriptions"].append(subscription)

    file_name = 'users.json'
    with open(file_name, 'w', encoding='utf-8') as json_file:
        json.dump(users, json_file, ensure_ascii=False)


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


def user_registration(token, pay_token, admin_id):
    bot = telebot.TeleBot(token, parse_mode=None)
    answers = {}
    allergies_answers = []
    user_info = {}
    allergies = {"nuts": "Орехи", "lactose": "Лактоза"}
    subscription_periods = ["1", "3", "6", "12"]
    one_meal_cost = 1

    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name if message.from_user.last_name else ''
        full_name = f'{first_name} {last_name}'
        user_info["first_name"] = first_name
        user_info["last_name"] = last_name or "no data"
        user_info["full_name"] = full_name
        print(user_info["last_name"])
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('Да', callback_data='user_name'),
            # types.InlineKeyboardButton('Другое имя', callback_data='custom_name')
        )
        bot.send_message(message.chat.id, f'Добрый день, {full_name}!\nМогу я дальше вас так называть или хотите ввести другое имя?', reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def answer(call):
        markup = types.InlineKeyboardMarkup(row_width=1)
        if call.message:
            if call.data == "custom_name":
                bot.answer_callback_query(call.id)
                bot.send_message(call.message.chat.id, "Отправьте мне ваши имя и фамилию:")
                if ' ' in call.message.text:
                    user_info["full_name"] = call.data
                    bot.send_message(call.message.chat.id, "Отправьте мне ваш контактный номер телефона:")
                    if call.message.text:
                        user_info["full_name"] = call.data
                        call.data = 'user_name'
            if call.data == "user_name":
                user_info["full_name"] = call.data or call.message.text
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
                answers["diet"] = call.data
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
                answers["meals_number"] = int(call.data[0])
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
                answers["persons_number"] = int(call.data[0])
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
            if call.data == "no_allergy" or call.data == "end_allergy":
                bot.answer_callback_query(call.id)
                for period in subscription_periods:
                    markup.add(
                        types.InlineKeyboardButton(period, callback_data=period)
                    )
                bot.send_message(call.message.chat.id, "Выберите срок подписки (месяцев):", reply_markup=markup)
                answers["allergies"] = allergies_answers
            if call.data in subscription_periods:
                bot.answer_callback_query(call.id)
                total_price = round(one_meal_cost * answers["meals_number"] * answers["persons_number"] * 30 * int(call.data) * (int(call.data) * 1 / (int(call.data) * 1.67)))
                markup.add(
                    types.InlineKeyboardButton("Отлично! Оформляем!", callback_data="/buy")
                )
                bot.send_message(call.message.chat.id, f"Стоимость вашей подписки составит: {total_price} руб.", reply_markup=markup)
                answers["total_price"] = total_price
                print(answers)
            if call.data == "/buy":
                print('нажал подписку')
                bot.answer_callback_query(call.id)
                bot.send_message(call.message.chat.id, 'Проверка тестовых платежей')
                price = types.LabeledPrice(label='Подписка на 1 месяц', amount=answers["total_price"]*100)
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

                    user_id = message.from_user.id
                    add_new_user(user_id, user_info["first_name"], user_info["last_name"], "+799912345678",
                                 message.successful_payment.telegram_payment_charge_id, answers["diet"],
                                 answers["meals_number"], answers["persons_number"],
                                 answers["allergies"])

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
                'Вы не являетесь зарегистрированным пользователем. Пожалуйста пройдите регистрацию!'
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

    bot.infinity_polling()


if __name__ == '__main__':
    load_dotenv()

    tg_token = os.getenv('TELEGRAM_BOT_TOKEN')
    pay_token = os.getenv('PAY_TOKEN')
    admin_id = os.getenv('ADMIN_ID')

    user_registration(tg_token, pay_token, admin_id)



