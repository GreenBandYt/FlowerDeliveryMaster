from django.core.management.base import BaseCommand
from telegram.ext import ApplicationBuilder, CommandHandler
from bot.handlers.common import start  # Импорт команды /start
from bot.handlers.common import link, get_registration_handler

import os
import logging
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Запускает Telegram-бота"

    def run(self):
        """Метод для запуска бота в отдельном процессе."""
        # Загрузка токена
        load_dotenv()
        token = os.getenv("TELEGRAM_BOT_TOKEN")

        if not token:
            logging.error("Ошибка: токен Telegram бота не найден.")
            return

        application = ApplicationBuilder().token(token).build()

        # Регистрация команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("link", link))
        application.add_handler(get_registration_handler())

        logging.info("Запуск Telegram-бота...")
        application.run_polling()
