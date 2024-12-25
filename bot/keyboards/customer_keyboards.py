#  bot/keyboards/customer_keyboards.py

from telegram import ReplyKeyboardMarkup

customer_keyboard = ReplyKeyboardMarkup(
    [
        ["📦 Мои заказы", "🛒 Корзина", "🛍️ Каталог", "ℹ️ Показать помощь"],
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)
