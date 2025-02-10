import logging
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from bot.handlers.admin import (
    handle_admin_users,
    handle_user_status_update_request,
    handle_admin_analytics,
    handle_cancel_manage_users
)

logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
AWAIT_TEXT = 1
AWAIT_USER_ID = 2
CHOOSE_PERIOD, EXIT_ANALYTICS = range(2)

# ConversationHandler для управления пользователями
manage_users_handler = ConversationHandler(
    entry_points=[CommandHandler("manage_users", handle_admin_users)],
    states={
        AWAIT_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_status_update_request)]
    },
    fallbacks=[CommandHandler("cancel", handle_cancel_manage_users)],
)

def register_admin_handlers(application):
    """
    Register handlers specific to the admin role.
    """
    logger.info("Registering admin-specific handlers...")

    # Регистрируем ConversationHandler для управления пользователями
    application.add_handler(manage_users_handler, group=0)
    logger.info("ConversationHandler for '/manage_users' registered.")

    # Регистрируем обработчик аналитики
    application.add_handler(CommandHandler("analytics", handle_admin_analytics), group=0)
    logger.info("Handler '/analytics' registered.")
