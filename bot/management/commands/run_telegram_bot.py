# bot/management/commands/run_telegram_bot.py
"""
run_telegram_bot.py

Описание:
Этот файл используется для запуска Telegram-бота в режиме разработки.
Бот автоматически запускается при старте Django сервера с помощью команды `python manage.py runserver`.

Особенности:
- Реализует интеграцию с Django через класс `BaseCommand`.
- Удобен для разработки, так как бот запускается одновременно с сервером разработки.
"""

import os
import logging
from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder
from bot.handlers.registration import register_handlers  # Используем централизованную регистрацию

import django
load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowerdelivery.settings')  # Путь к вашим настройкам Django
django.setup()

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Запускает Telegram-бота"

    def run(self):
        """Метод для запуска бота."""
        token = os.getenv("TELEGRAM_BOT_TOKEN")

        if not token:
            logger.error("Ошибка: токен Telegram бота не найден.")
            return

        # Инициализация приложения
        application = ApplicationBuilder().token(token).build()

        # Регистрация хэндлеров
        logger.info("Регистрация хэндлеров...")
        register_handlers(application)

        logger.info("Запуск Telegram-бота. Ожидание команд...")
        application.run_polling()

    def handle(self, *args, **options):
        # Стандартный метод handle вызывает run()
        self.run()
