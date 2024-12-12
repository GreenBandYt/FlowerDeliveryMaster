import os
import asyncio
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler
from bot.bot_logic import start, link, get_registration_handler  # Импортируем команды и обработчики

# Загрузка токена
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def run_bot():
    """
    Асинхронная функция для запуска Telegram-бота.
    """
    try:
        print("Инициализация Telegram-бота...")
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("link", link))
        application.add_handler(get_registration_handler())  # Добавляем обработчик регистрации
        print("Бот успешно запущен и ожидает команды...")
        await application.run_polling()
    except Exception as e:
        print(f"Произошла ошибка при запуске бота: {e}")

def start_bot():
    """
    Запуск Telegram-бота с созданием нового цикла событий.
    """
    try:
        print("Запуск Telegram-бота...")
        loop = asyncio.new_event_loop()  # Создаем новый цикл событий
        asyncio.set_event_loop(loop)    # Устанавливаем цикл событий для текущего потока
        loop.run_until_complete(run_bot())  # Запускаем выполнение асинхронной функции
    except Exception as e:
        print(f"Ошибка при запуске Telegram-бота: {e}")
    finally:
        print("Завершение работы Telegram-бота.")
