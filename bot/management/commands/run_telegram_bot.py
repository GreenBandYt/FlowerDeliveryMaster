# bot/management/commands/run_telegram_bot.py

import os
import logging
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

import django
load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowerdelivery.settings')  # Путь к вашим настройкам Django
django.setup()

from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from bot.handlers.common import start, link, get_registration_handler, my_orders, get_my_orders_handler, help
from bot.handlers.customer import view_orders, view_catalog, add_to_cart, remove_from_cart, view_cart, checkout, confirm_checkout, cancel_checkout

from bot.bot_logic import (
    orders, order_details, update_order_status,
    manage_users, update_user_is_staff, update_user_status_callback,
    take_order,  # Обработчик кнопки "Взять в работу"
    get_analytics_handler  # Обработчик аналитики
)

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Определение состояний для команд
AWAIT_ORDER_ID = 1
AWAIT_USER_ID = 2  # Состояние для команды /manage_users


class Command(BaseCommand):
    help = "Запускает Telegram-бота"

    def run(self):
        """Метод для запуска бота в отдельном процессе."""
        token = os.getenv("TELEGRAM_BOT_TOKEN")

        if not token:
            logger.error("Ошибка: токен Telegram бота не найден.")
            return

        # Инициализация приложения
        application = ApplicationBuilder().token(token).build()

        # Добавляем хэндлеры
        logger.info("Добавление команд и обработчиков...")

        # Основные команды
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help))
        application.add_handler(CommandHandler("link", link))
        application.add_handler(CommandHandler("my_orders", my_orders))
        application.add_handler(CommandHandler("view_orders", view_orders))
        application.add_handler(CommandHandler("view_catalog", view_catalog))  # Просмотр каталога
        application.add_handler(CommandHandler("add_to_cart", add_to_cart))  # Добавление в корзину
        application.add_handler(CommandHandler("view_cart", view_cart))  # Просмотр корзины
        application.add_handler(CommandHandler("checkout", checkout))  # Оформление заказа

        application.add_handler(get_my_orders_handler())

        # Обработчик для /orders с состояниями
        orders_handler = ConversationHandler(
            entry_points=[CommandHandler("orders", orders)],
            states={
                AWAIT_ORDER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_details)],
            },
            fallbacks=[]
        )
        application.add_handler(orders_handler)

        # Обработчик inline-кнопок для смены статуса заказа
        application.add_handler(CallbackQueryHandler(update_order_status, pattern=r"^status_\d+_.+$"))

        # Обработчик для /manage_users с состояниями
        manage_users_handler = ConversationHandler(
            entry_points=[CommandHandler("manage_users", manage_users)],
            states={
                AWAIT_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_user_is_staff)],
            },
            fallbacks=[]
        )
        application.add_handler(manage_users_handler)

        # Callback-обработчик для смены статуса is_staff
        application.add_handler(CallbackQueryHandler(update_user_status_callback, pattern=r"^staff_\d+_(true|false)$"))

        # Callback-обработчик для кнопки "Взять в работу"
        application.add_handler(CallbackQueryHandler(take_order, pattern=r"^take_order_\d+$"))

        # Обработчик регистрации (если есть)
        application.add_handler(get_registration_handler())

        # Обработчик аналитики
        application.add_handler(get_analytics_handler())

        # Callback обработчики для управления корзиной
        application.add_handler(CallbackQueryHandler(add_to_cart, pattern=r"^add_to_cart_\d+$"))
        application.add_handler(CallbackQueryHandler(remove_from_cart, pattern=r"^remove_from_cart_\d+$"))
        application.add_handler(CallbackQueryHandler(checkout, pattern="^checkout$"))
        application.add_handler(CallbackQueryHandler(confirm_checkout, pattern="^confirm_checkout$"))
        application.add_handler(CallbackQueryHandler(cancel_checkout, pattern="^cancel_checkout$"))

        # Обработчик текстовых сообщений для кнопок-эмодзи
        async def handle_menu_buttons(update, context):
            """
            Обрабатывает текстовые сообщения, которые соответствуют эмодзи на кнопках.
            """
            text = update.message.text.strip()

            if text == "📦":  # Просмотр заказов
                await view_orders(update, context)
            elif text == "🛒":  # Просмотр корзины
                await view_cart(update, context)
            elif text == "🛍️":  # Просмотр каталога
                await view_catalog(update, context)
            elif text == "ℹ️":  # Помощь
                await help(update, context)
            else:
                await update.message.reply_text("Я не понимаю эту команду. Попробуйте ещё раз.")

        # Добавляем обработчик текстовых сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons))

        logger.info("Запуск Telegram-бота. Ожидание команд...")
        application.run_polling()

    def handle(self, *args, **options):
        # Стандартный метод handle вызывает run()
        self.run()
