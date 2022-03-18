import os

import telebot
from telebot import types
from dotenv import load_dotenv

import keyboard as kb

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
        bot.send_message(message.chat.id, 'Добро пожаловать в личный кабинет')
        bot.send_message(message.chat.id, "Для проверки статуса подписки нажмите на кнопку", reply_markup=kb.inline_kb_full)


    @bot.callback_query_handler(func=lambda call: True)
    def process_check_subs(callback_query):
        answer = callback_query.data
        if answer == 'check_subs':
            bot.answer_callback_query(callback_query.id)
            bot.send_message(callback_query.from_user.id, 'Подписка оформлена!')
        elif answer == 'get_recipe':
            bot.answer_callback_query(callback_query.id)
            bot.send_message(callback_query.from_user.id, 'Рецепт блюда из меню')
        elif answer == 'get_shopping_list':
            bot.answer_callback_query(callback_query.id)
            bot.send_message(callback_query.from_user.id, 'Список покупок')


    bot.infinity_polling(skip_pending=True)



def main():
    load_dotenv()

    tg_token = os.getenv('BOT_TOKEN')
    pay_token = os.getenv('PAY_TOKEN')

    user_payment(tg_token, pay_token)


if __name__ == '__main__':
    main()
