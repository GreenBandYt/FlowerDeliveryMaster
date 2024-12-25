# bot/handlers/reg_admin.py

import logging
from telegram.ext import CommandHandler, CallbackQueryHandler
from bot.handlers.admin import (
    manage_users, get_analytics_handler, update_user_status_callback, orders, admin_help, look_help, show_help, analytics
)

logger = logging.getLogger(__name__)

def register_admin_handlers(application):
    """
    Register handlers specific to the admin role.
    """
    # Command handlers
    application.add_handler(CommandHandler("orders", orders))
    logger.info("Handler '/orders' registered.")

    # Analytics handler
    application.add_handler(get_analytics_handler())
    logger.info("Analytics ConversationHandler registered.")

    # Inline callback handlers for user management
    application.add_handler(CallbackQueryHandler(update_user_status_callback, pattern=r"^staff_\d+_(true|false)$"))
    logger.info("Handler for user status change callbacks registered.")

    application.add_handler(CallbackQueryHandler(manage_users, pattern="^manage_users$"))
    logger.info("Handler for manage users inline callbacks registered.")

    application.add_handler(CommandHandler("admin_help", admin_help))
    logger.info("Handler '/admin_help' registered.")

    application.add_handler(CommandHandler("look_help", look_help))
    logger.info("Handler '/look_help' registered.")

    application.add_handler(CommandHandler("show_help", show_help))
    logger.info("Handler '/show_help' registered.")

    application.add_handler(CommandHandler("analytics", analytics))
    logger.info("Handler '/analytics' registered.")

    application.add_handler(CommandHandler("manage_users", manage_users))
    logger.info("Handler '/manage_users' registered.")

    application.add_handler(CommandHandler("admin_help", admin_help))

    application.add_handler(CommandHandler("orders", orders))
    logger.info("Handler '/orders' registered.")





