import os
import asyncio
import logging
from dotenv import load_dotenv
import django

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'myproject.settings')  # Замените myproject.settings на ваш файл настроек
django.setup()

from telegram.ext import ApplicationBuilder, CommandHandler
from bot.bot_logic import start, link, orders, get_registration_handler  # Импортируем команды и обработчики

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загрузка токена
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TOKEN:
    logger.error("Ошибка: токен Telegram бота не найден. Проверьте файл .env.")
    exit(1)


async def run_bot():
    """
    Асинхронная функция для запуска Telegram-бота.
    """
    try:
        logger.info("Инициализация Telegram-бота...")
        application = ApplicationBuilder().token(TOKEN).build()

        # Добавляем обработчики
        logger.info("Добавление команд и обработчиков...")

        # Сначала основные команды
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("link", link))
        application.add_handler(CommandHandler("orders", orders))  # Управление заказами

        # Затем уже регистрация (ConversationHandler)
        # application.add_handler(get_registration_handler())  # Обработчик регистрации

        logger.info("Запуск Telegram-бота. Ожидание команд...")
        await application.run_polling()
    except Exception as e:
        logger.error(f"Произошла ошибка при запуске бота: {e}", exc_info=True)


def start_bot():
    """
    Запуск Telegram-бота с созданием нового цикла событий.
    """
    try:
        logger.info("Запуск Telegram-бота...")
        loop = asyncio.new_event_loop()  # Создаем новый цикл событий
        asyncio.set_event_loop(loop)  # Устанавливаем цикл событий для текущего потока
        loop.run_until_complete(run_bot())  # Запускаем выполнение асинхронной функции
    except Exception as e:
        logger.error(f"Ошибка при запуске Telegram-бота: {e}", exc_info=True)
    finally:
        logger.info("Завершение работы Telegram-бота.")


if __name__ == '__main__':
    start_bot()
