# bot/handlers/reg_customer.py

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.handlers.customer import (
    view_orders, view_catalog, view_cart, checkout, handle_customer_menu,
    add_to_cart, remove_from_cart, confirm_checkout, cancel_checkout,
    decrease_quantity, increase_quantity, delete_item
)

# Настройка логгера
logger = logging.getLogger(__name__)

def register_customer_handlers(application: ApplicationBuilder):
    """
    Регистрация обработчиков для клиентов.
    """
    # --- Команды ---
    application.add_handler(CommandHandler("view_orders", view_orders))
    logger.info("Команда /view_orders зарегистрирована.")

    application.add_handler(CommandHandler("view_catalog", view_catalog))
    logger.info("Команда /view_catalog зарегистрирована.")

    application.add_handler(CommandHandler("view_cart", view_cart))
    logger.info("Команда /view_cart зарегистрирована.")

    application.add_handler(CommandHandler("checkout", checkout))
    logger.info("Команда /checkout зарегистрирована.")

    # --- Меню ---
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_customer_menu))
    logger.info("Обработчик текстового меню клиентов зарегистрирован.")

    # --- Inline-кнопки ---
    application.add_handler(CallbackQueryHandler(add_to_cart, pattern=r"^add_to_cart_\d+$"))
    logger.info("Обработчик inline-кнопок для добавления в корзину зарегистрирован.")

    application.add_handler(CallbackQueryHandler(remove_from_cart, pattern=r"^remove_from_cart_\d+$"))
    logger.info("Обработчик inline-кнопок для удаления из корзины зарегистрирован.")

    application.add_handler(CallbackQueryHandler(confirm_checkout, pattern="^confirm_checkout$"))
    logger.info("Обработчик inline-кнопок для подтверждения оформления заказа зарегистрирован.")

    application.add_handler(CallbackQueryHandler(cancel_checkout, pattern="^cancel_checkout$"))
    logger.info("Обработчик inline-кнопок для отмены оформления заказа зарегистрирован.")

    application.add_handler(CallbackQueryHandler(decrease_quantity, pattern=r"^decrease_\d+$"))
    application.add_handler(CallbackQueryHandler(increase_quantity, pattern=r"^increase_\d+$"))
    application.add_handler(CallbackQueryHandler(delete_item, pattern=r"^delete_\d+$"))
    logger.info("Обработчики inline-кнопок для управления корзиной зарегистрированы.")
