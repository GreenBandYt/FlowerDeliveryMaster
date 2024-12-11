import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder
from bot.bot_logic import start, link, get_registration_handler  # Импорт команд и обработчика регистрации

# Загрузка токена
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def start_bot():
    """
    Функция для запуска Telegram-бота.
    """
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("link", link))
    application.add_handler(get_registration_handler())  # Получаем обработчик регистрации
    application.run_polling()
