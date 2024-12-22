# bot/handlers/reg_common.py

import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from bot.handlers.common import start, admin_help, look_help, show_help, link, get_registration_handler

# Настройка логгера
logger = logging.getLogger(__name__)

def register_common_handlers(application: ApplicationBuilder):
    """
    Регистрация общих обработчиков.
    """
    # Команда /start
    application.add_handler(CommandHandler("start", start))
    logger.info("Команда /start зарегистрирована.")

    # Команда /admin_help
    application.add_handler(CommandHandler("admin_help", admin_help))
    logger.info("Команда /admin_help зарегистрирована.")

    # Команда /look_help
    application.add_handler(CommandHandler("look_help", look_help))
    logger.info("Команда /look_help зарегистрирована.")

    # Команда /show_help
    application.add_handler(CommandHandler("show_help", show_help))
    logger.info("Команда /show_help зарегистрирована.")

    # Команда /link
    application.add_handler(CommandHandler("link", link))
    logger.info("Команда /link зарегистрирована.")

    # Регистрация ConversationHandler для регистрации /register
    application.add_handler(get_registration_handler())
    logger.info("Обработчик для /register зарегистрирован.")
