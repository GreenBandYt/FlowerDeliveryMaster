# bot/handlers/reg_staff.py

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.handlers.staff import (
    my_orders, update_order_status, handle_staff_menu, complete_order_callback,
    take_order
)

# Настройка логгера
logger = logging.getLogger(__name__)

def register_staff_handlers(application: ApplicationBuilder):
    """
    Регистрация обработчиков для сотрудников.
    """
    # --- Команды ---
    application.add_handler(CommandHandler("my_orders", my_orders))
    logger.info("Команда /my_orders зарегистрирована.")

    application.add_handler(CommandHandler("update_status", update_order_status))
    logger.info("Команда /update_status зарегистрирована.")

    # --- Меню ---
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_staff_menu))
    logger.info("Обработчик текстового меню сотрудников зарегистрирован.")

    # --- Inline-кнопки ---
    application.add_handler(CallbackQueryHandler(complete_order_callback, pattern=r"^complete_order_\d+$"))
    logger.info("Обработчик callback-кнопок для завершения заказа зарегистрирован.")

    application.add_handler(CallbackQueryHandler(take_order, pattern=r"^take_order_\d+$"))
    logger.info("Обработчик inline-кнопок для кнопки 'Взять в работу' зарегистрирован.")

    application.add_handler(CallbackQueryHandler(update_order_status, pattern=r"^status_\d+_.+$"))
    logger.info("Обработчик inline-кнопок для смены статуса заказа зарегистрирован.")
