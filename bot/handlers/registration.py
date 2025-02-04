# bot/handlers/registration.py

import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Import role-specific handler registration functions
from bot.handlers.reg_common import register_common_handlers
from bot.handlers.reg_admin import register_admin_handlers
from bot.handlers.reg_customer import register_customer_handlers
from bot.handlers.reg_staff import register_staff_handlers
from bot.handlers.reg_new_user import register_new_user_handlers  # Добавлено для новой роли


def register_handlers(application):
    """
    Centralized handler registration
    """
    logger.info("Starting handler registration...")

    try:
        logger.info("Registering new user handlers...")
        register_new_user_handlers(application)  # Регистрация обработчиков для незарегистрированных пользователей
        logger.info("New user handlers registered.")
    except Exception as e:
        logger.error(f"Error registering new user handlers: {e}")

    try:
        logger.info("Registering common handlers...")
        register_common_handlers(application)
        logger.info("Common handlers registered.")
    except Exception as e:
        logger.error(f"Error registering common handlers: {e}")

    try:
        logger.info("Registering admin handlers...")
        register_admin_handlers(application)
        logger.info("Admin handlers registered.")
    except Exception as e:
        logger.error(f"Error registering admin handlers: {e}")

    try:
        logger.info("Registering customer handlers...")
        register_customer_handlers(application)
        logger.info("Customer handlers registered.")
    except Exception as e:
        logger.error(f"Error registering customer handlers: {e}")

    try:
        logger.info("Registering staff handlers...")
        register_staff_handlers(application)
        logger.info("Staff handlers registered.")
    except Exception as e:
        logger.error(f"Error registering staff handlers: {e}")

    logger.info("Handler registration process completed successfully.")
