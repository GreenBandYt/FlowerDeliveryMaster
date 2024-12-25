# bot/handlers/reg_customer.py

import logging
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.handlers.customer import (
    view_orders, view_catalog, view_cart, checkout, handle_customer_menu,
    add_to_cart, remove_from_cart, confirm_checkout, cancel_checkout,
    decrease_quantity, increase_quantity, delete_item
)
from bot.handlers.admin import (
    analytics, manage_users, orders
)

logger = logging.getLogger(__name__)

def register_customer_handlers(application):
    """
    Register handlers specific to the customer role.
    """
    # Command handlers
    application.add_handler(CommandHandler("view_orders", view_orders))
    logger.info("Handler '/view_orders' registered.")

    application.add_handler(CommandHandler("view_catalog", view_catalog))
    logger.info("Handler '/view_catalog' registered.")

    application.add_handler(CommandHandler("view_cart", view_cart))
    logger.info("Handler '/view_cart' registered.")

    application.add_handler(CommandHandler("checkout", checkout))
    logger.info("Handler '/checkout' registered.")

    application.add_handler(CommandHandler("analytics", analytics))
    logger.info("Handler '/analytics' registered.")

    application.add_handler(CommandHandler("manage_users", manage_users))
    logger.info("Handler '/manage_users' registered.")

    application.add_handler(CommandHandler("orders", orders))
    logger.info("Handler '/orders' registered.")




    # Menu handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_customer_menu))
    logger.info("Customer menu handler registered.")

    # Inline callback handlers
    application.add_handler(CallbackQueryHandler(add_to_cart, pattern=r"^add_to_cart_\d+$"))
    logger.info("Handler for adding to cart callbacks registered.")

    application.add_handler(CallbackQueryHandler(remove_from_cart, pattern=r"^remove_from_cart_\d+$"))
    logger.info("Handler for removing from cart callbacks registered.")

    application.add_handler(CallbackQueryHandler(confirm_checkout, pattern="^confirm_checkout$"))
    logger.info("Handler for confirm checkout callbacks registered.")

    application.add_handler(CallbackQueryHandler(cancel_checkout, pattern="^cancel_checkout$"))
    logger.info("Handler for cancel checkout callbacks registered.")

    application.add_handler(CallbackQueryHandler(decrease_quantity, pattern=r"^decrease_\d+$"))
    logger.info("Handler for decreasing item quantity callbacks registered.")

    application.add_handler(CallbackQueryHandler(increase_quantity, pattern=r"^increase_\d+$"))
    logger.info("Handler for increasing item quantity callbacks registered.")

    application.add_handler(CallbackQueryHandler(delete_item, pattern=r"^delete_\d+$"))
    logger.info("Handler for deleting item callbacks registered.")

    application.add_handler(CallbackQueryHandler(checkout, pattern="^checkout$"))
    logger.info("Handler for checkout callback registered.")
