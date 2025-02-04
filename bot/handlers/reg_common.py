# bot/handlers/reg_common.py

import logging
from bot.handlers.common import start  # Импортируем универсальный обработчик

logger = logging.getLogger(__name__)

def register_common_handlers(application):
    """
    Register common handlers
    """
    # Регистрируем обработчик для /start через универсальный обработчик
    application.add_handler(CommandHandler("start", start))
    logger.info("Handler '/start' registered.")
