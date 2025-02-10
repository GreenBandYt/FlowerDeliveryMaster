# bot/handlers/registration.py

import logging
from telegram.ext import MessageHandler, CallbackQueryHandler, CommandHandler, filters

# Импорты универсальных обработчиков
from bot.handlers.common import handle_user_input, handle_inline_buttons, start
# Импорт специфичных обработчиков (например, для команды /start)
from bot.handlers.admin import admin_start

# Настройка логгера
logger = logging.getLogger(__name__)

def register_handlers(application):
    """
    Центральная регистрация обработчиков.
    """

    logger.info("Начинается регистрация обработчиков...")

    # Регистрация универсального обработчика текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))
    logger.info("Универсальный обработчик текстовых сообщений зарегистрирован.")

    # Регистрация универсального обработчика инлайн-кнопок
    application.add_handler(CallbackQueryHandler(handle_inline_buttons))
    logger.info("Универсальный обработчик инлайн-кнопок зарегистрирован.")

    # Регистрация специфичного обработчика для команды /start
    application.add_handler(CommandHandler("start", start))
    logger.info("Обработчик команды /start зарегистрирован.")

    logger.info("Регистрация обработчиков завершена успешно.")
