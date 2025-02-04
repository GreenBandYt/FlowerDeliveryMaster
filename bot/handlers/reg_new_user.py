# bot/handlers/reg_new_user.py

import logging
from telegram.ext import CommandHandler, MessageHandler, filters
from bot.handlers.new_user import (
    new_user_start,
    help_new_user,
    link,
    get_registration_handler,
)

logger = logging.getLogger(__name__)

def register_new_user_handlers(application):
    """
    Register handlers specific to new (unregistered) users.
    """
    # Командные обработчики

    # УБРАТЬ /start, чтобы не было двойной регистрации.
    # application.add_handler(CommandHandler("start", new_user_start))
    # logger.info("Handler '/start' registered for new users.")

    application.add_handler(CommandHandler("help_new_user", help_new_user))
    logger.info("Handler '/help_new_user' registered.")

    application.add_handler(CommandHandler("link", link))
    logger.info("Handler '/link' registered for new users.")

    # ConversationHandler для /register
    application.add_handler(get_registration_handler())
    logger.info("Conversation handler for '/register' registered.")

    # Обработчик текстовых сообщений (кнопок меню) удалён, теперь это обработает common.py.
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_user_menu))
    # logger.info("Message handler for new user menu interaction registered.")
