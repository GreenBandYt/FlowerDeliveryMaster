# bot/handlers/reg_customer.py

import logging
from telegram.ext import CommandHandler, CallbackQueryHandler
from bot.handlers.customer import (
    view_orders, view_catalog, view_cart, checkout,
    add_to_cart, remove_from_cart, confirm_checkout, cancel_checkout,
    decrease_quantity, increase_quantity, delete_item
)

logger = logging.getLogger(__name__)

def register_customer_handlers(application):
    """
    Register handlers specific to the customer role.
    """
    # --- Командные обработчики ---
    application.add_handler(CommandHandler("view_orders", view_orders))
    logger.info("Registered command handler: '/view_orders' for viewing orders.")

    application.add_handler(CommandHandler("view_catalog", view_catalog))
    logger.info("Registered command handler: '/view_catalog' for viewing the catalog.")

    application.add_handler(CommandHandler("view_cart", view_cart))
    logger.info("Registered command handler: '/view_cart' for viewing the cart.")

    application.add_handler(CommandHandler("checkout", checkout))
    logger.info("Registered command handler: '/checkout' for starting checkout.")

    # --- Inline-обработчики для корзины ---
    application.add_handler(CallbackQueryHandler(add_to_cart, pattern=r"^add_to_cart_\d+$"))
    logger.info("Registered callback handler: 'add_to_cart' for adding items to the cart.")

    application.add_handler(CallbackQueryHandler(remove_from_cart, pattern=r"^remove_from_cart_\d+$"))
    logger.info("Registered callback handler: 'remove_from_cart' for removing items from the cart.")

    application.add_handler(CallbackQueryHandler(confirm_checkout, pattern="^confirm_checkout$"))
    logger.info("Registered callback handler: 'confirm_checkout' for confirming checkout.")

    application.add_handler(CallbackQueryHandler(cancel_checkout, pattern="^cancel_checkout$"))
    logger.info("Registered callback handler: 'cancel_checkout' for canceling checkout.")

    application.add_handler(CallbackQueryHandler(decrease_quantity, pattern=r"^decrease_\d+$"))
    logger.info("Registered callback handler: 'decrease_quantity' for decreasing item quantity.")

    application.add_handler(CallbackQueryHandler(increase_quantity, pattern=r"^increase_\d+$"))
    logger.info("Registered callback handler: 'increase_quantity' for increasing item quantity.")

    application.add_handler(CallbackQueryHandler(delete_item, pattern=r"^delete_\d+$"))
    logger.info("Registered callback handler: 'delete_item' for deleting items from the cart.")

    application.add_handler(CallbackQueryHandler(checkout, pattern="^checkout$"))
    logger.info("Registered callback handler: 'checkout' for proceeding to checkout.")
