#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import time
import requests
import logging
from multiprocessing import Process
import django

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def wait_for_server(url, retries=10, delay=2):
    """Проверяет доступность сервера по указанному URL."""
    for attempt in range(retries):
        try:
            logging.info(f"Попытка {attempt + 1}/{retries}: проверка доступности сервера {url}.")
            response = requests.get(url)
            if response.status_code == 200:
                logging.info("Сервер доступен.")
                return True
        except requests.exceptions.ConnectionError as e:
            logging.warning(f"Сервер недоступен. Ждём {delay} секунд. Ошибка: {e}")
            time.sleep(delay)
    logging.error("Сервер не запустился. Завершаем работу.")
    return False


def run_bot():
    """Функция для запуска Telegram-бота."""
    try:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowerdelivery.settings")
        django.setup()
        from bot.management.commands.run_telegram_bot import Command
        bot_command = Command()
        bot_command.run()
        logging.info("Telegram-бот успешно запущен.")
    except Exception as e:
        logging.error(f"Ошибка при запуске Telegram-бота: {e}", exc_info=True)


def run_server():
    """Запускает сервер Django."""
    logging.info("Запуск сервера Django.")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowerdelivery.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "runserver"])


def main():
    """Главная функция."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowerdelivery.settings")
    if "runserver" in sys.argv:
        # Проверяем, что это основной процесс
        if os.environ.get('RUN_MAIN') == 'true':
            logging.info("Это перезапуск сервера Django. Логика запуска бота пропущена.")
            run_server()
            return

        # Запускаем сервер в отдельном процессе
        server_process = Process(target=run_server)
        server_process.start()

        # Ждём готовности сервера
        if wait_for_server("http://127.0.0.1:8000"):
            logging.info("Сервер готов. Запускаем Telegram-бота.")
            bot_process = Process(target=run_bot)
            bot_process.start()
            bot_process.join()
        else:
            logging.error("Сервер не запустился. Завершаем работу.")
            server_process.terminate()
            sys.exit(1)
    else:
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
