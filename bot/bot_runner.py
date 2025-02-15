# bot/bot_runner.py
"""
bot_runner.py

Описание:
Этот файл используется для запуска Telegram-бота в режиме продакшена.
Бот запускается как отдельный асинхронный процесс, независимый от сервера Django.

Особенности:
- Используется отдельный цикл событий для управления ботом.
- Рекомендуется для развертывания на сервере в продакшене, где бот работает автономно.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
import django

# Инициализация Django
load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowerdelivery.settings')  # Укажите ваш файл настроек
django.setup()

from telegram.ext import ApplicationBuilder

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def run_bot():
    """
    Асинхронная функция для запуска Telegram-бота.
    """
    try:
        # Загрузка токена из файла окружения
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            logger.error("Ошибка: токен Telegram бота не найден. Проверьте файл .env.")
            return

        logger.info("Инициализация Telegram-бота...")
        application = ApplicationBuilder().token(token).build()

        # Импорт обработчиков из регистрационного файла
        from bot.handlers.registration import register_handlers
        register_handlers(application)

        logger.info("Запуск Telegram-бота. Ожидание команд...")
        await application.run_polling()

    except Exception as e:
        logger.error(f"Произошла ошибка при запуске бота: {e}", exc_info=True)


def start_bot():
    """
    Запуск Telegram-бота с созданием нового цикла событий.
    """
    try:
        logger.info("Запуск Telegram-бота...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_bot())
    except Exception as e:
        logger.error(f"Ошибка при запуске Telegram-бота: {e}", exc_info=True)
    finally:
        logger.info("Завершение работы Telegram-бота.")


if __name__ == '__main__':
    start_bot()
