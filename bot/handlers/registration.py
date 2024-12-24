# bot/handlers/registration.py

import logging
from telegram import ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters




# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Состояния для ConversationHandler
AWAIT_ORDER_ID = 1
AWAIT_USER_ID = 2


def register_handlers(application):
    """
    Регистрирует все обработчики для Telegram-бота.
    """
    from bot.handlers.common import start, link, cancel, admin_help, look_help, show_help
    from bot.handlers.admin import manage_users, update_user_is_staff, update_user_status_callback, orders, order_details, update_order_status
    from bot.handlers.customer import view_orders, view_cart, view_catalog
    from bot.handlers.staff import my_orders, take_order, complete_order_callback

    # Общие команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("link", link))
    application.add_handler(CommandHandler("cancel", cancel))

    # Помощь
    application.add_handler(CommandHandler("admin_help", admin_help))
    application.add_handler(CommandHandler("look_help", look_help))
    application.add_handler(CommandHandler("show_help", show_help))

    # Администраторские команды
    application.add_handler(CommandHandler("manage_users", manage_users))
    application.add_handler(CommandHandler("orders", orders))

    # Клиентские команды
    application.add_handler(CommandHandler("view_orders", view_orders))
    application.add_handler(CommandHandler("view_cart", view_cart))
    application.add_handler(CommandHandler("view_catalog", view_catalog))

    # Сотрудники
    application.add_handler(CommandHandler("my_orders", my_orders))

    # CallbackQueryHandler (универсальный)
    application.add_handler(CallbackQueryHandler(update_user_status_callback))
    application.add_handler(CallbackQueryHandler(complete_order_callback))

    logger.info("Все обработчики успешно зарегистрированы.")
