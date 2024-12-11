from django.apps import AppConfig
import threading  # Для запуска бота в отдельном потоке


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'

    def ready(self):
        """
        Запуск Telegram-бота в отдельном потоке после полной загрузки приложения.
        """
        from . import bot_runner  # Импортируем функцию для запуска бота внутри ready
        threading.Thread(target=bot_runner.start_bot, daemon=True).start()
