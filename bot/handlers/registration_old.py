# # bot/handlers/registration_old.py
#
# import logging
# from telegram import ReplyKeyboardRemove
# from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
# from bot.handlers.common import start, show_help,look_help, admin_help, link, get_registration_handler
# from bot.handlers.customer import (
#     view_orders, view_catalog, add_to_cart, remove_from_cart,
#     view_cart, checkout, confirm_checkout, cancel_checkout,
#     handle_customer_menu, decrease_quantity, increase_quantity, delete_item
# )
# from bot.bot_logic import (
#     orders, order_details, update_order_status,
#     manage_users, update_user_is_staff, update_user_status_callback,
#     take_order, get_analytics_handler
# )
# from bot.handlers.staff import handle_staff_menu, complete_order_callback, my_orders, update_order_status
# from bot.handlers.staff import handle_staff_menu
# from bot.handlers.staff import complete_order_callback
#
# # Настройка логгера
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)
#
# # Состояния для ConversationHandler
# AWAIT_ORDER_ID = 1
# AWAIT_USER_ID = 2
#
# def register_handlers(application: ApplicationBuilder):
#
#     # ======== ОБЩИЕ КОМАНДЫ ========
#     # Команда /start
#     application.add_handler(CommandHandler("start", start))
#     logger.info("Команда /start зарегистрирована.")
#
#     # Команда /show_help
#     application.add_handler(CommandHandler("show_help", show_help))
#     logger.info("Команда /show_help  зарегистрирована.")
#
#     # Команда /look_help
#     application.add_handler(CommandHandler("look_help", look_help))
#     logger.info("Команда /look_help  зарегистрирована.")
#
#     # Команда /admin_help
#     application.add_handler(CommandHandler("admin_help", admin_help))
#     logger.info("Команда /admin_help  зарегистрирована.")
#
#
#
#     # Команда /link
#     application.add_handler(CommandHandler("link", link))
#     logger.info("Команда /link зарегистрирована.")
#
#     # Регистрация ConversationHandler для /register
#     application.add_handler(get_registration_handler())
#     logger.info("Обработчик регистрации /register зарегистрирован.")
#
#     # ======== ОБРАБОТЧИКИ ДЛЯ КЛИЕНТОВ ========
#     # --- Команды ---
#     application.add_handler(CommandHandler("view_orders", view_orders))
#     logger.info("Команда /view_orders зарегистрирована.")
#
#     application.add_handler(CommandHandler("view_catalog", view_catalog))
#     logger.info("Команда /view_catalog зарегистрирована.")
#
#     application.add_handler(CommandHandler("view_cart", view_cart))
#     logger.info("Команда /view_cart зарегистрирована.")
#
#     application.add_handler(CommandHandler("checkout", checkout))
#     logger.info("Команда /checkout зарегистрирована.")
#
#     # --- МЕНЮ-КНОПКИ ---
#     # Место для кнопок меню клиента (ReplyKeyboardMarkup)
#     # Регистрация обработчика текстового меню клиента
#     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_customer_menu))
#     logger.info("Обработчик текстового меню клиента зарегистрирован.")
#
#     # --- INLINE-КНОПКИ ---
#     application.add_handler(CallbackQueryHandler(add_to_cart, pattern=r"^add_to_cart_\d+$"))
#     logger.info("Обработчик inline-кнопок для добавления в корзину зарегистрирован.")
#     application.add_handler(CallbackQueryHandler(remove_from_cart, pattern=r"^remove_from_cart_\d+$"))
#     logger.info("Обработчик inline-кнопок для удаления из корзины зарегистрирован.")
#     application.add_handler(CallbackQueryHandler(checkout, pattern="^checkout$"))
#     logger.info("Обработчик inline-кнопок для оформления заказа зарегистрирован.")
#     application.add_handler(CallbackQueryHandler(confirm_checkout, pattern="^confirm_checkout$"))
#     logger.info("Обработчик inline-кнопок для подтверждения оформления заказа зарегистрирован.")
#     application.add_handler(CallbackQueryHandler(cancel_checkout, pattern="^cancel_checkout$"))
#     logger.info("Обработчик inline-кнопок для отмены оформления заказа зарегистрирован.")
#
#     # Регистрация обработчиков управления корзиной
#     application.add_handler(CallbackQueryHandler(decrease_quantity, pattern=r"^decrease_\d+$"))
#     application.add_handler(CallbackQueryHandler(increase_quantity, pattern=r"^increase_\d+$"))
#     application.add_handler(CallbackQueryHandler(delete_item, pattern=r"^delete_\d+$"))
#
#     # ======== ОБРАБОТЧИКИ ДЛЯ СОТРУДНИКОВ ========
#
#     # --- Команды ---
#     orders_handler = ConversationHandler(
#         entry_points=[CommandHandler("orders", orders)],
#         states={
#             AWAIT_ORDER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_details)],
#         },
#         fallbacks=[]
#     )
#
#     # Добавляем регистрацию обработчиков для сотрудников
#     # --- Команды ---
#     application.add_handler(CommandHandler("my_orders", my_orders))
#     logger.info("Команда /my_orders зарегистрирована.")
#
#     application.add_handler(CommandHandler("update_status", update_order_status))
#     logger.info("Команда /update_status зарегистрирована.")
#
#     application.add_handler(
#         CommandHandler("show_help", handle_staff_menu))  # Возможно, вы используете `handle_staff_menu` для помощи
#     logger.info("Команда /show_help зарегистрирована.")
#
#     application.add_handler(orders_handler)
#     logger.info("Обработчик для команды /orders зарегистрирован.")
#
#     # Регистрация обработчиков callback-кнопок для завершения и отмены заказа
#     application.add_handler(CallbackQueryHandler(complete_order_callback, pattern=r"^complete_order_\d+$"))
#     logger.info("Обработчик callback-кнопок для завершения заказа зарегистрирован.")
#
#     # --- МЕНЮ-КНОПКИ ДЛЯ СОТРУДНИКОВ ---
#     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_staff_menu))
#     logger.info("Обработчик текстового меню сотрудников зарегистрирован.")
#
#     # --- INLINE-КНОПКИ ---
#     application.add_handler(CallbackQueryHandler(update_order_status, pattern=r"^status_\d+_.+$"))
#     logger.info("Обработчик inline-кнопок для смены статуса заказа зарегистрирован.")
#     application.add_handler(CallbackQueryHandler(take_order, pattern=r"^take_order_\d+$"))
#     logger.info("Обработчик inline-кнопок для кнопки 'Взять в работу' зарегистрирован.")
#
#     # ======== ОБРАБОТЧИКИ ДЛЯ АДМИНИСТРАТОРОВ ========
#     # --- Команды ---
#     application.add_handler(get_analytics_handler())
#     logger.info("Обработчик аналитики зарегистрирован.")
#
#     # --- МЕНЮ-КНОПКИ ---
#     # Место для кнопок меню администратора (ReplyKeyboardMarkup)
#
#     # --- INLINE-КНОПКИ ---
#     application.add_handler(CallbackQueryHandler(update_user_status_callback, pattern=r"^staff_\d+_(true|false)$"))
#     logger.info("Обработчик inline-кнопок для смены статуса пользователя зарегистрирован.")
#     application.add_handler(CallbackQueryHandler(manage_users, pattern="^manage_users$"))
#     logger.info("Обработчик inline-кнопок для управления пользователями зарегистрирован.")
#
#
