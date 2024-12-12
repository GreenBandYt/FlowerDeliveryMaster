from django.apps import AppConfig


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'

    def ready(self):
        """
        Никакой логики для запуска бота в данный момент
        """
        pass
