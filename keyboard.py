from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

inline_kb_full = InlineKeyboardMarkup(row_width=1)

check_subs = InlineKeyboardButton("Проверить статус подписки", callback_data='check_subs')
get_recipe = InlineKeyboardButton('Получить рецепт', callback_data='get_recipe')
get_shopping_list = InlineKeyboardButton('Получить список покупок', callback_data='get_shipping_list')


inline_kb_full.add(check_subs, get_recipe, get_shopping_list)
