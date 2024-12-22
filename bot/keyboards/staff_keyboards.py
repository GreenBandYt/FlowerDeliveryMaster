# bot/keyboards/staff_keyboards.py

from telegram import ReplyKeyboardMarkup

staff_keyboard = ReplyKeyboardMarkup(
    [["📦 Текущие заказы", "🔄 Обновить статус", "ℹ️ Помощь посмотреть"]],
    resize_keyboard=True,
    one_time_keyboard=False
)
