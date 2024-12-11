from django.core.management.base import BaseCommand
from bot.bot_logic import main
import asyncio

class Command(BaseCommand):
    help = "Запускает Telegram-бота"

    def handle(self, *args, **kwargs):
        self.stdout.write("Запуск Telegram-бота...")
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            self.stdout.write("\nОстановка Telegram-бота.")
