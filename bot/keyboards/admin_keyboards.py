# bot/keyboards/admin_keyboards.py

from telegram import ReplyKeyboardMarkup

admin_keyboard = ReplyKeyboardMarkup(
    [["📊 Аналитика", "👥 Пользователи", "📦 Заказы", "ℹ️ Помощь"]],
    resize_keyboard=True,
    one_time_keyboard=False
)