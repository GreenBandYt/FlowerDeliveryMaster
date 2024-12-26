# bot/handlers/registration.py

import logging

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def register_handlers(application):
    """
    Centralized handler registration
    """
    logger.info("Importing role-specific handler registration functions.")
    from bot.handlers.reg_common import register_common_handlers
    from bot.handlers.reg_admin import register_admin_handlers
    from bot.handlers.reg_customer import register_customer_handlers
    from bot.handlers.reg_staff import register_staff_handlers

    # Register handlers for different user roles and common commands
    logger.info("Starting handler registration...")

    # Log start and end of each registration process
    logger.info("Registering common handlers...")
    register_common_handlers(application)
    logger.info("Common handlers registered.")

    logger.info("Registering admin handlers...")
    register_admin_handlers(application)
    logger.info("Admin handlers registered.")

    logger.info("Registering customer handlers...")
    register_customer_handlers(application)
    logger.info("Customer handlers registered.")

    logger.info("Registering staff handlers...")
    register_staff_handlers(application)
    logger.info("Staff handlers registered.")

    logger.info("All handlers successfully registered.")
