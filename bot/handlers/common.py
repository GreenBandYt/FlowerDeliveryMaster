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
from bot.handlers.admin import admin_start
from bot.handlers.admin import (analytics_today, analytics_week, analytics_month, analytics_year, analytics_all_time, analytics_cancel)

from bot.handlers.staff import staff_start
from bot.handlers.customer import customer_start

from bot.handlers.new_user import new_user_start

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
    logger.info(f"📩 /start от пользователя {telegram_id}")

    try:
        user = await sync_to_async(CustomUser.objects.filter(telegram_id=telegram_id).first)()

        if user:
            role = "admin" if user.is_superuser else "staff" if user.is_staff else "customer"
            logger.info(f"✅ Пользователь найден: {user.username}, роль: {role}")

            if user.is_superuser:
                await admin_start(update, context, user)
            elif user.is_staff:
                await staff_start(update, context)
            else:
                await customer_start(update, context)
        else:
            logger.warning(f"⚠️ Пользователь с Telegram ID {telegram_id} не найден в БД.")
            await new_user_start(update, context)

    except Exception as e:
        logger.error(f"❌ Ошибка в start(): {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")


# ======== Универсальный обработчик текста ========
async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Универсальный обработчик текста от пользователя.
    """
    if context.user_data.get("state") is not None:
        logger.info(f"⏳ Пропускаем текст: активное состояние {context.user_data['state']}")
        return

    user_text = update.message.text.strip()
    telegram_id = update.effective_user.id
    logger.info(f"📨 Текст от {telegram_id}: {user_text}")

    role = cache.get(f"user_role_{telegram_id}")
    if not role:
        user = await sync_to_async(CustomUser.objects.filter(telegram_id=telegram_id).first)()
        if user:
            role = "admin" if user.is_superuser else "manager" if user.is_staff else "customer"
            cache.set(f"user_role_{telegram_id}", role, timeout=3600)
        else:
            role = "new_user"

    logger.info(f"🔍 Определена роль: {role}")

    action = TEXT_ACTIONS.get(user_text)
    if action:
        logger.info(f"✅ Найден обработчик текста: {action.__name__} для команды '{user_text}'")
        await action(update, context)
        return

    logger.warning(f"⚠️ Неизвестная команда: '{user_text}' от {telegram_id}")
    await update.message.reply_text(
        "Извините, я вас не понял. Попробуйте уточнить запрос или воспользуйтесь кнопками меню. 🤔"
    )


# ======== Универсальный обработчик inline-кнопок ========
async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Универсальный обработчик для инлайн-кнопок (без парсинга ':').
    """
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    logger.info(f"🔍 Получен callback_data: {callback_data}")

    action_func = CALLBACK_ACTIONS.get(callback_data)  # 👈 Теперь ищем просто по ключу

    if action_func:
        logger.info(f"✅ Найден обработчик: {action_func.__name__} для callback_data={callback_data}")

        try:
            await action_func(update, context)  # 👈 Теперь вызываем просто без параметров
        except Exception as e:
            logger.error(f"❌ Ошибка при выполнении '{callback_data}': {e}", exc_info=True)
            await query.edit_message_text("❌ Ошибка при выполнении действия. Обратитесь к администратору.")
    else:
        logger.warning(f"⚠️ Неизвестное callback_data: {callback_data}")
        await query.edit_message_text("⚠️ Кнопка больше не активна. Попробуйте снова или обратитесь к администратору.")

