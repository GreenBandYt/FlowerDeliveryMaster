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
from bot.handlers.common import start, link, get_registration_handler
from bot.bot_logic import (
    orders, order_details, update_order_status,
    manage_users, update_user_is_staff, update_user_status_callback,
    take_order  # Импортируем обработчик кнопки "Взять в работу"
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
        application.add_handler(CommandHandler("link", link))

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
        # Этот обработчик используется для уведомлений о взятии заказа в работу
        application.add_handler(CallbackQueryHandler(take_order, pattern=r"^take_order_\d+$"))

        # Обработчик регистрации (если есть)
        application.add_handler(get_registration_handler())

        logger.info("Запуск Telegram-бота. Ожидание команд...")
        application.run_polling()

    def handle(self, *args, **options):
        # Стандартный метод handle вызывает run()
        self.run()
