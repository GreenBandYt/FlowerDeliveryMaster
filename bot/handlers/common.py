# bot/handlers/common.py

import logging
from telegram import Update
from telegram.ext import ContextTypes
from users.models import CustomUser
from asgiref.sync import sync_to_async
from bot.dictionaries.text_actions import TEXT_ACTIONS
from bot.dictionaries.smart_replies import TEXT_RESPONSES
from bot.dictionaries.smart_replies import get_smart_reply
from bot.dictionaries.callback_actions import CALLBACK_ACTIONS
from bot.utils.callback_parser import parse_callback_data  # Новый парсер
from django.core.cache import cache
from bot.handlers.admin import admin_start
from bot.handlers.admin import (
    update_user_status_callback,
    analytics_today,
    analytics_week,
    analytics_month,
    analytics_year,
    analytics_all_time,
    analytics_cancel,
    cancel_user_status_callback,
    handle_orders_by_status_new,
    handle_orders_processing,
    handle_orders_completed,
    handle_order_details,
    handle_set_executor,
    handle_admin_orders,
)
from bot.handlers.admin import (handle_user_status_update_request, cancel_user_status_callback,)

from bot.handlers.staff import (staff_start,
    handle_staff_new_orders,
    handle_staff_take_order,
    handle_staff_my_orders,
    complete_order_callback,
    cancel_order_callback,
    handle_staff_help,
    )

from bot.handlers.customer import (
    customer_start,
    handle_customer_help,
    handle_customer_catalog,
    customer_add_to_cart,
    customer_view_cart,
    customer_decrease_quantity,
    customer_increase_quantity,
    customer_remove_from_cart,
    customer_view_checkout,
    customer_confirm_checkout,
    customer_cancel_order,
    customer_view_orders,
    customer_repeat_order,
    )

from bot.handlers.new_user import (
    new_user_start,
    handle_new_user_help,
    handle_new_user_link_start,
    handle_new_user_link_input,
    handle_new_user_get_username,
    handle_new_user_get_password,
    handle_new_user_get_phone,
    handle_new_user_get_address,

    )

from bot.utils.access_control import check_access

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

STATE_HANDLERS = {
    "USERNAME": handle_new_user_get_username,
    "PASSWORD": handle_new_user_get_password,
    "PHONE": handle_new_user_get_phone,
    "ADDRESS": handle_new_user_get_address,
}

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
    user_text = update.message.text.strip()
    telegram_id = update.effective_user.id

    # ✅ Если бот ждёт ввод ID пользователя
    if context.user_data.get("state") == "AWAIT_USER_ID":
        logger.info(f"📥 Передаём в handle_user_status_update_request: {user_text}")
        await handle_user_status_update_request(update, context)
        return

    # ✅ Если бот ждёт ввод логина для привязки аккаунта
    if context.user_data.get("state") == "AWAIT_LINK":
        logger.info(f"📥 Передаём в handle_new_user_link_input: {user_text}")
        await handle_new_user_link_input(update, context)
        return

    # ✅ Если бот находится в одном из шагов регистрации
    if context.user_data.get("state") in STATE_HANDLERS:
        current_state = context.user_data.get("state")
        logger.info(f"📥 Обработка регистрации: состояние {current_state} для пользователя {telegram_id}")
        await STATE_HANDLERS[current_state](update, context)
        return

    logger.info(f"📨 Текст от {telegram_id}: {user_text}")

    # Проверяем роль пользователя (с кешированием для оптимизации)
    role = cache.get(f"user_role_{telegram_id}")
    if not role:
        user = await sync_to_async(CustomUser.objects.filter(telegram_id=telegram_id).first)()
        if user:
            role = "admin" if user.is_superuser else "manager" if user.is_staff else "customer"
            cache.set(f"user_role_{telegram_id}", role, timeout=3600)
        else:
            role = "new_user"

    logger.info(f"🔍 Определена роль: {role}")

    # ✅ Если текст совпадает с командой в TEXT_ACTIONS
    action = TEXT_ACTIONS.get(user_text)
    if action:
        logger.info(f"✅ Найден обработчик текста: {action.__name__} для команды '{user_text}'")
        await action(update, context)
        return

    # ✅ Если команда не найдена, ищем умный ответ
    smart_reply = get_smart_reply(user_text)
    if smart_reply != TEXT_RESPONSES["default"]:
        logger.info(f"🤖 Умный ответ: {smart_reply}")
        await update.message.reply_text(smart_reply)
        return

    # ✅ Если ничего не найдено – отправляем стандартное сообщение
    logger.warning(f"⚠️ Неизвестная команда: '{user_text}' от {telegram_id}")
    await update.message.reply_text(
        "Извините, я вас не понял. Попробуйте уточнить запрос или воспользуйтесь кнопками меню. 🤔"
    )


# ======== Универсальный обработчик inline-кнопок ========
async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Универсальный обработчик для инлайн-кнопок (с поддержкой динамических callback'ов).
    """
    query = update.callback_query
    await query.answer()

    callback_data = query.data
    logger.info(f"🔍 Получен callback_data: {callback_data}")

    # 🔹 Проверяем точное совпадение
    action_func = CALLBACK_ACTIONS.get(callback_data)

    # 🔹 Если нет точного совпадения, ищем динамический обработчик (например, user_status_update:19:true)
    if not action_func:
        for key in CALLBACK_ACTIONS.keys():
            if callback_data.startswith(key):  # Если начало совпадает
                action_func = CALLBACK_ACTIONS[key]
                break

    if action_func:
        logger.info(f"✅ Найден обработчик: {action_func.__name__} для callback_data={callback_data}")

        try:
            await action_func(update, context)  # Вызываем без передачи параметров
        except Exception as e:
            logger.error(f"❌ Ошибка при выполнении '{callback_data}': {e}", exc_info=True)
            await query.edit_message_text("❌ Ошибка при выполнении действия. Обратитесь к администратору.")
    else:
        logger.warning(f"⚠️ Неизвестное callback_data: {callback_data}")
        await query.edit_message_text("⚠️ Кнопка больше не активна. Попробуйте снова или обратитесь к администратору.")
