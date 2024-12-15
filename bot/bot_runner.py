import os
import asyncio
from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)
from bot.handlers.common import start, link, get_registration_handler
from bot.handlers.customer import view_orders
import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка токена
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def run_bot():
    """
    Асинхронная функция для запуска Telegram-бота.
    """
    try:
        # Инициализация Telegram-бота
        logger.info("Инициализация Telegram-бота...")
        application = ApplicationBuilder().token(TOKEN).build()

        # Регистрация основных команд
        logger.info("Регистрация команд...")
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("link", link))
        application.add_handler(CommandHandler("view_orders", view_orders))  # Команда /view_orders
        application.add_handler(get_registration_handler())

        # Проверка и логирование зарегистрированных обработчиков
        registered_handlers = [
            h for group in application.handlers.values() for h in group
        ]
        logger.info(f"Зарегистрированные обработчики: {[str(handler) for handler in registered_handlers]}")

        # Отладочный MessageHandler для обработки непредвиденных сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, debug_message_handler))

        # Запуск бота
        logger.info("Запуск Telegram-бота...")
        await application.run_polling()
    except Exception as e:
        logger.error(f"Произошла ошибка при запуске бота: {e}", exc_info=True)

def debug_message_handler(update, context):
    """
    Обработчик для отладки: перехватывает все текстовые сообщения, которые не являются командами.
    """
    logger.warning(f"Перехвачено сообщение: {update.message.text} от пользователя {update.effective_user.id}")

def start_bot():
    """
    Запуск Telegram-бота с созданием нового цикла событий.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_bot())
    except Exception as e:
        logger.error(f"Ошибка при запуске Telegram-бота: {e}", exc_info=True)
    finally:
        logger.info("Завершение работы Telegram-бота.")
