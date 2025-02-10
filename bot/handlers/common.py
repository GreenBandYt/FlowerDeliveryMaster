# bot/handlers/common.py

import logging
from telegram import Update
from telegram.ext import ContextTypes
from users.models import CustomUser
from asgiref.sync import sync_to_async
from bot.dictionaries.text_actions import TEXT_ACTIONS
from bot.dictionaries.callback_actions import CALLBACK_ACTIONS
from bot.utils.callback_parser import parse_callback_data  # Новый парсер
from django.core.cache import cache

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ======== Обработчик команды /start ========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start. Приветствует пользователя в зависимости от его роли
    и добавляет меню с кнопками.
    """
    telegram_id = update.effective_user.id
    try:
        user = await sync_to_async(CustomUser.objects.filter(telegram_id=telegram_id).first)()

        if user:
            logger.info(f"Пользователь найден: {user.username}, superuser={user.is_superuser}, staff={user.is_staff}")
            if user.is_superuser:
                await admin_start(update, context)
            elif user.is_staff:
                await staff_start(update, context)
            else:
                await customer_start(update, context)
        else:
            logger.warning(f"Пользователь с Telegram ID {telegram_id} не найден.")
            await new_user_start(update, context)
    except Exception as e:
        logger.error(f"Ошибка при обработке команды /start: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

# ======== Универсальный обработчик текста ========
async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Универсальный обработчик текста от пользователя.
    """
    if context.user_data.get("state") is not None:
        logger.info("Активное состояние обнаружено в context.user_data, пропускаем универсальный обработчик.")
        return

    user_text = update.message.text.strip()
    telegram_id = update.effective_user.id

    role = cache.get(f"user_role_{telegram_id}")
    if not role:
        user = await sync_to_async(CustomUser.objects.filter(telegram_id=telegram_id).first)()
        if user:
            role = "admin" if user.is_superuser else "manager" if user.is_staff else "customer"
            cache.set(f"user_role_{telegram_id}", role, timeout=3600)
        else:
            role = "new_user"

    action = TEXT_ACTIONS.get(user_text)
    if action:
        await action(update, context)
        return

    await update.message.reply_text(
        "Извините, я вас не понял. Попробуйте уточнить запрос или воспользуйтесь кнопками меню. 🤔"
    )

# ======== Универсальный обработчик inline-кнопок ========
async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Универсальный обработчик для инлайн-кнопок.
    """
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    action, params = parse_callback_data(callback_data)
    logger.info(f"Получено callback_data: action={action}, params={params}")

    action_func = CALLBACK_ACTIONS.get(action)
    if action_func:
        try:
            await action_func(update, context, *params)
        except Exception as e:
            logger.error(f"Ошибка при выполнении действия для '{callback_data}': {e}", exc_info=True)
            await query.edit_message_text(
                "Произошла ошибка при выполнении действия. Обратитесь к администратору."
            )
    else:
        logger.warning(f"Неизвестное callback_data: {callback_data}")
        await query.edit_message_text(
            "Кнопка больше не активна. Попробуйте снова или обратитесь к администратору."
        )
