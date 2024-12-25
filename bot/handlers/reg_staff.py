import logging
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.handlers.staff import (
    my_orders, update_order_status, handle_staff_menu, complete_order_callback,
    take_order
)

logger = logging.getLogger(__name__)

def register_staff_handlers(application):
    """
    Register handlers specific to the staff role.
    """
    # Command handlers
    application.add_handler(CommandHandler("my_orders", my_orders))
    logger.info("Handler '/my_orders' registered.")

    application.add_handler(CommandHandler("update_status", update_order_status))
    logger.info("Handler '/update_status' registered.")

    # Menu handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_staff_menu))
    logger.info("Staff menu handler registered.")

    # Inline callback handlers
    application.add_handler(CallbackQueryHandler(complete_order_callback, pattern=r"^complete_order_\d+$"))
    logger.info("Handler for completing order callbacks registered.")

    application.add_handler(CallbackQueryHandler(take_order, pattern=r"^take_order_\d+$"))
    logger.info("Handler for taking order callbacks registered.")

    application.add_handler(CallbackQueryHandler(update_order_status, pattern=r"^status_\d+_.+$"))
    logger.info("Handler for updating order status callbacks registered.")
