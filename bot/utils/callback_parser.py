# bot/utils/callback_parser.py

import logging

# Создаём логгер
logger = logging.getLogger(__name__)

def parse_callback_data(callback_data):
    try:
        parts = callback_data.split(":")
        action = parts[0]
        params = parts[1:] if len(parts) > 1 else []

        # Логируем парсинг callback_data
        logger.debug(f"🔍 Парсинг callback_data: {callback_data} → action={action}, params={params}")

        return action, params
    except Exception as e:
        logger.error(f"❌ Ошибка в parse_callback_data: {e}")
        return None, []
