# # bot/handlers/reg_staff.py
#
# import logging
# from telegram.ext import CommandHandler, CallbackQueryHandler
# from bot.handlers.staff import (
#     my_orders, update_order_status, complete_order_callback, take_order, look_help
# )
#
# logger = logging.getLogger(__name__)
#
# def register_staff_handlers(application):
#     """
#     Register handlers specific to the staff role.
#     """
#     # --- Командные обработчики ---
#     application.add_handler(CommandHandler("my_orders", my_orders))
#     logger.info("Registered command handler: '/my_orders' for viewing orders.")
#
#     application.add_handler(CommandHandler("update_status", update_order_status))
#     logger.info("Registered command handler: '/update_status' for updating order status.")
#
#     application.add_handler(CommandHandler("look_help", look_help))
#     logger.info("Registered command handler: '/look_help' for staff help.")
#
#     # --- Inline-обработчики ---
#     application.add_handler(CallbackQueryHandler(complete_order_callback, pattern=r"^complete_order_\d+$"))
#     logger.info("Registered callback handler: 'complete_order' for completing orders.")
#
#     application.add_handler(CallbackQueryHandler(take_order, pattern=r"^take_order_\d+$"))
#     logger.info("Registered callback handler: 'take_order' for taking orders.")
#
#     application.add_handler(CallbackQueryHandler(update_order_status, pattern=r"^status_\d+_.+$"))
#     logger.info("Registered callback handler: 'update_order_status' for updating order statuses.")
