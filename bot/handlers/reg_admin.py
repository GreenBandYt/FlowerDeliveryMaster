# bot/handlers/reg_admin.py

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from bot.handlers.admin import manage_users, get_analytics_handler, update_user_status_callback

# Настройка логгера
logger = logging.getLogger(__name__)

def register_admin_handlers(application: ApplicationBuilder):
    """
    Регистрация обработчиков для администраторов.
    """
    # Команда аналитики
    application.add_handler(get_analytics_handler())
    logger.info("Обработчик аналитики зарегистрирован.")

    # Inline-кнопки для управления пользователями
    application.add_handler(CallbackQueryHandler(update_user_status_callback, pattern=r"^staff_\d+_(true|false)$"))
    logger.info("Обработчик inline-кнопок для смены статуса пользователя зарегистрирован.")

    application.add_handler(CallbackQueryHandler(manage_users, pattern="^manage_users$"))
    logger.info("Обработчик inline-кнопок для управления пользователями зарегистрирован.")
