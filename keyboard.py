from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

inline_kb_full = InlineKeyboardMarkup(row_width=1)
check_subs = InlineKeyboardButton("Проверить статус подписки", callback_data='subscription')
get_recipe = InlineKeyboardButton('Получить рецепт', callback_data='recipe')
get_shopping_list = InlineKeyboardButton('Получить список покупок', callback_data='shopping_list')
inline_kb_full.add(check_subs, get_recipe, get_shopping_list)

markup_kb_full = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
account_btn = KeyboardButton('/account')
markup_kb_full.add(account_btn)
