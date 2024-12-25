# bot/handlers/reg_common.py

import logging
from telegram.ext import CommandHandler
from bot.handlers.common import start, admin_help, look_help, show_help, link, get_registration_handler

logger = logging.getLogger(__name__)

def register_common_handlers(application):
    """
    Register common handlers
    """
    application.add_handler(CommandHandler("start", start))
    logger.info("Handler '/start' registered.")

    application.add_handler(CommandHandler("admin_help", admin_help))
    logger.info("Handler '/admin_help' registered.")

    application.add_handler(CommandHandler("look_help", look_help))
    logger.info("Handler '/look_help' registered.")

    application.add_handler(CommandHandler("show_help", show_help))
    logger.info("Handler '/show_help' registered.")

    application.add_handler(CommandHandler("link", link))
    logger.info("Handler '/link' registered.")

    application.add_handler(get_registration_handler())
    logger.info("Conversation handler for '/register' registered.")
