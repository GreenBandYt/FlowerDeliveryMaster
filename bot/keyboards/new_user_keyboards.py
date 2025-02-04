# bot/keyboards/new_user_keyboards.py

from telegram import ReplyKeyboardMarkup

new_user_keyboard = ReplyKeyboardMarkup(
    [
        ["🔗 Привязать аккаунт", "📝 Зарегистрироваться"],
        ["🆘 Помощь"]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
