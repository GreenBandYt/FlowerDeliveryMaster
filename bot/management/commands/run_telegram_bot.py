import os
import logging
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

import django
load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowerdelivery.settings')  # Заменили на flowerdelivery.settings
django.setup()

from telegram.ext import ApplicationBuilder, CommandHandler
from bot.handlers.common import start, link, get_registration_handler
from bot.bot_logic import orders  # Импорт команды /orders

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Запускает Telegram-бота"

    def run(self):
        """Метод для запуска бота в отдельном процессе."""
        token = os.getenv("TELEGRAM_BOT_TOKEN")

        if not token:
            logger.error("Ошибка: токен Telegram бота не найден.")
            return

        # Инициализация приложения
        application = ApplicationBuilder().token(token).build()

        # Добавляем хэндлеры
        logger.info("Добавление команд и обработчиков...")

        # Сначала основные команды
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("link", link))
        application.add_handler(CommandHandler("orders", orders))  # Управление заказами

        # Затем регистрация
        application.add_handler(get_registration_handler())

        logger.info("Запуск Telegram-бота. Ожидание команд...")
        application.run_polling()

    def handle(self, *args, **options):
        # Стандартный метод handle вызывает run()
        self.run()
