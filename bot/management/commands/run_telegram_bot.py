from django.core.management.base import BaseCommand
from telegram.ext import ApplicationBuilder, CommandHandler
from bot.handlers.common import start
from bot.handlers.common import link, get_registration_handler

import os
import tempfile
import logging
from dotenv import load_dotenv

# Файл-флаг для проверки состояния бота
# Динамическое определение пути для временного файла
BOT_LOCK_FILE = os.path.join(tempfile.gettempdir(), "telegram_bot.lock")


class Command(BaseCommand):
    help = "Запускает Telegram-бота"

    def run(self):
        """Метод для запуска бота в отдельном процессе."""
        # Проверяем, запущен ли уже бот
        if os.path.exists(BOT_LOCK_FILE):
            logging.error("Telegram-бот уже запущен. Проверьте активные процессы.")
            return

        try:
            # Создаём файл-флаг
            with open(BOT_LOCK_FILE, "w") as f:
                f.write("locked")

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
        except Exception as e:
            logging.error(f"Ошибка при запуске Telegram-бота: {e}", exc_info=True)
        finally:
            # Удаляем файл-флаг после завершения работы
            if os.path.exists(BOT_LOCK_FILE):
                os.remove(BOT_LOCK_FILE)
            logging.info("Telegram-бот завершил работу.")
