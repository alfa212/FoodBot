import os

import telebot
from telebot import types
from dotenv import load_dotenv


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
                start_parameter='1-month-subsription-example',
                invoice_payload='some-invoice-payload-for-our-internal-use'
            )


        @bot.pre_checkout_query_handler(func=lambda query: True)
        def process_pre_checkout_query(pre_checkout_query):
            bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


        @bot.message_handler(content_types=['SUCCESSFUL_PAYMENT'])
        def process_successful_payment(message):
            print('successful_payment:')
            pmnt = message.successfull_payment.to_python()
            for key, val in pmnt.items():
                print(f'{key} = {val}')

            bot.send_message(message.chat.id,
                             f'successfull_payment: '
                             f'{message.successfull_payment.total_amount // 100} '
                             f'{message.successfull_payment.currency}'
                             )


    bot.infinity_polling()



def main():
    load_dotenv()

    tg_token = os.getenv('BOT_TOKEN')
    pay_token = os.getenv('PAY_TOKEN')

    user_payment(tg_token, pay_token)


if __name__ == '__main__':
    main()
