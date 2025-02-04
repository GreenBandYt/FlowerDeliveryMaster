# bot/handlers/reg_admin.py

import logging
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler

from bot.handlers.admin import (
    manage_users, get_analytics_handler, orders, admin_help, analytics, update_order_status, update_user_status_callback, cancel_manage_users
)


logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
AWAIT_USER_ID = 1

# ConversationHandler для управления пользователями
manage_users_handler = ConversationHandler(
    entry_points=[CommandHandler("manage_users", manage_users)],
    states={AWAIT_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_user_is_staff)]},
    fallbacks=[CommandHandler("cancel", cancel_manage_users)],
)


def register_admin_handlers(application):
    """
    Register handlers specific to the admin role.
    """
    # Командные хендлеры
    application.add_handler(CommandHandler("admin_help", admin_help))
    logger.info("Handler '/admin_help' registered.")

    application.add_handler(CommandHandler("orders", orders))
    logger.info("Handler '/orders' registered.")

    application.add_handler(CommandHandler("analytics", analytics))
    logger.info("Handler '/analytics' registered.")

    # ConversationHandler для управления пользователями
    application.add_handler(manage_users_handler)
    logger.info("ConversationHandler for '/manage_users' registered.")

    # ConversationHandler для аналитики
    application.add_handler(get_analytics_handler())
    logger.info("Analytics ConversationHandler registered.")

    # Inline-обработчики для управления пользователями
    application.add_handler(CallbackQueryHandler(update_user_status_callback, pattern=r"^staff_\d+_(true|false)$"))
    logger.info("Handler for user status change callbacks registered.")

    application.add_handler(CallbackQueryHandler(update_user_status_callback, pattern=r"^cancel_user_status_\d+$"))
    logger.info("Handler for cancel user status callbacks registered.")

    # Inline-обработчики для управления заказами
    application.add_handler(CallbackQueryHandler(update_order_status, pattern=r"^status_\d+_(new|processing|completed)$"))
    logger.info("Handler for order status change callbacks registered.")

    application.add_handler(CallbackQueryHandler(update_order_status, pattern=r"^cancel_order_status_\d+$"))
    logger.info("Handler for cancel order status callbacks registered.")
