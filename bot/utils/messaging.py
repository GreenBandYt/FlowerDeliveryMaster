import logging
from telegram.ext import CallbackContext

# Логгер
logger = logging.getLogger(__name__)


async def send_message(context: CallbackContext, telegram_id: int, text: str):
    """
    Отправляет сообщение пользователю в Telegram.
    :param context: Контекст бота.
    :param telegram_id: ID пользователя в Telegram.
    :param text: Текст сообщения.
    """
    try:
        bot = context.bot  # Получаем объект бота напрямую
        if not hasattr(bot, "send_message"):
            raise AttributeError("Переданный context.bot не содержит метод send_message")

        await bot.send_message(chat_id=telegram_id, text=text)
        logger.info(f"✅ Сообщение успешно отправлено пользователю {telegram_id}")

    except Exception as e:
        logger.error(f"❌ Ошибка при отправке сообщения пользователю {telegram_id}: {e}", exc_info=True)
