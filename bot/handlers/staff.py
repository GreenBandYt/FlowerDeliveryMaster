# bot/handlers/staff.py

import os
from PIL import Image
from telegram.constants import ParseMode  # Для HTML-разметки сообщений
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from asgiref.sync import sync_to_async
from prettytable import PrettyTable
from users.models import CustomUser
from catalog.models import Order, OrderItem
from bot.keyboards.staff_keyboards import staff_keyboard
import logging
import asyncio
from telegram.ext import Application

from pathlib import Path
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from PIL import Image
import logging
from asgiref.sync import sync_to_async

# Настройка логгера
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
AWAIT_ORDER_ID = 1
AWAIT_NEW_STATUS = 2

# ✅ Перевод статусов заказов
STATUS_TRANSLATION = {
    "created": "Новый",
    "processing": "В процессе",
    "shipped": "Отправлен",
    "delivered": "Доставлен",
    "canceled": "Отменён"
}
# from bot.utils.access_control import check_access  # Декоратор для проверки роли

async def staff_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Приветствие сотрудника. Проверяет, является ли пользователь сотрудником.
    """
    telegram_id = update.effective_user.id
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id)

        logger.info(f"[STAFF] Пользователь {telegram_id} вошел в систему как сотрудник.")

        # ✅ Отправляем приветственное сообщение
        await update.message.reply_text(
            f"🛠️ Здравствуйте, {user.username} (Сотрудник)!\n"
            "🔧 Доступные команды:\n"
            "📦 Новые заказы\n"
            "🔄 Текущие заказы\n"
            "❓ Помощь",
            reply_markup=staff_keyboard
        )

    except CustomUser.DoesNotExist:
        logger.error(f"❌ Ошибка: пользователь с Telegram ID {telegram_id} не найден.")
        await update.message.reply_text("❌ У вас нет доступа к этой команде.")
    except Exception as e:
        logger.error(f"❌ Ошибка в staff_start: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")

# ======= Просмотр новых заказов =======
async def handle_staff_new_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Отображение списка новых заказов (которые еще никто не взял в работу).
    """
    telegram_id = update.effective_user.id
    try:
        # ✅ Получаем сотрудника
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id, is_staff=True)
        logger.info(f"[STAFF] Пользователь {telegram_id} запросил список новых заказов.")

        # ✅ Фильтруем только заказы без исполнителя
        orders = await sync_to_async(lambda: list(Order.objects.filter(status="created", executor_id__isnull=True)))()

        if not orders:
            logger.warning(f"❌ Нет доступных заказов для пользователя {telegram_id}.")
            await update.message.reply_text("❌ Нет доступных заказов в системе.")
            return ConversationHandler.END

        # ✅ Формируем список заказов с кнопками "Взять в работу"
        for order in orders:
            translated_status = STATUS_TRANSLATION.get(order.status, "Неизвестный статус")
            message = (
                f"📦 <b>Заказ #{order.id}</b>\n"
                f"💰 Сумма: {order.total_price:.2f} ₽\n"
                f"📍 Адрес: {order.address or 'Не указан'}\n"
                f"📌 Статус: <b>{translated_status}</b>\n\n"
            )

            # ✅ Кнопка "Взять в работу" (правильный callback_data)
            keyboard = [[InlineKeyboardButton("🛠 Взять в работу", callback_data=f"staff_take_order:{order.id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)

        logger.info(f"✅ Отправлен список из {len(orders)} новых заказов пользователю {telegram_id}.")
        return ConversationHandler.END

    except CustomUser.DoesNotExist:
        logger.error(f"❌ Ошибка: сотрудник с Telegram ID {telegram_id} не найден.")
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"❌ Ошибка в handle_staff_new_orders: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
        return ConversationHandler.END

# ======= Берем заказ в работу =======
async def handle_staff_take_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Позволяет сотруднику взять заказ в работу (назначает исполнителем).
    """
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    callback_data = query.data  # Получаем callback_data

    # ✅ Проверяем, что callback соответствует ожидаемому формату
    parts = callback_data.split(":")
    if len(parts) != 2 or parts[0] != "staff_take_order":
        logger.warning(f"❌ Некорректный callback_data: {callback_data}")
        return

    order_id = int(parts[1])  # ✅ Извлекаем ID заказа

    try:
        # ✅ Получаем сотрудника
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id, is_staff=True)

        # ✅ Проверяем, есть ли заказ и не занят ли он
        order = await sync_to_async(Order.objects.get)(id=order_id)

        if order.executor_id is not None:
            logger.warning(f"❌ Заказ #{order_id} уже взят в работу другим сотрудником.")
            await query.edit_message_text(f"❌ Этот заказ уже взял в работу другой сотрудник.")
            return

        # ✅ Назначаем сотрудника исполнителем и обновляем статус заказа
        order.executor_id = user.id
        order.status = "processing"
        await sync_to_async(order.save)()

        logger.info(f"✅ Пользователь {telegram_id} взял заказ #{order_id} в работу.")
        await query.edit_message_text(f"✅ Вы взяли заказ #{order_id} в работу.")

    except Order.DoesNotExist:
        logger.error(f"❌ Ошибка: заказ #{order_id} не найден.")
        await query.edit_message_text("❌ Ошибка: заказ не найден.")

    except CustomUser.DoesNotExist:
        logger.error(f"❌ Ошибка: сотрудник с Telegram ID {telegram_id} не найден.")
        await query.edit_message_text("❌ У вас нет прав для выполнения этой команды.")

    except Exception as e:
        logger.error(f"❌ Ошибка в handle_staff_take_order: {e}", exc_info=True)
        await query.edit_message_text("❌ Произошла ошибка. Попробуйте позже.")

# ======= Просмотр текущих заказов =======
async def handle_staff_my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Отображение заказов сотрудника (которые он выполняет).
    """
    telegram_id = update.effective_user.id
    try:
        # ✅ Получаем сотрудника
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id, is_staff=True)
        logger.info(f"[STAFF] Пользователь {telegram_id} запросил список своих заказов в работе.")

        # ✅ Фильтруем заказы, где сотрудник - исполнитель
        orders = await sync_to_async(lambda: list(Order.objects.filter(status="processing", executor_id=user.id)))()

        if not orders:
            logger.warning(f"❌ У сотрудника {telegram_id} нет активных заказов.")
            await update.message.reply_text("❌ У вас нет активных заказов в работе.")
            return ConversationHandler.END

        # ✅ Формируем список заказов с кнопками "ℹ️ Подробнее"
        for order in orders:
            translated_status = STATUS_TRANSLATION.get(order.status, "Неизвестный статус")
            message = (
                f"📦 <b>Заказ #{order.id}</b>\n"
                f"💰 Сумма: {order.total_price:.2f} ₽\n"
                f"📍 Адрес: {order.address or 'Не указан'}\n"
                f"📌 Статус: <b>{translated_status}</b>\n\n"
            )

            # ✅ Кнопка "ℹ️ Подробнее" (правильный callback_data)
            keyboard = [[InlineKeyboardButton("ℹ️ Подробнее", callback_data=f"staff_order_details:{order.id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)

        logger.info(f"✅ Отправлен список из {len(orders)} заказов в работе пользователю {telegram_id}.")
        return ConversationHandler.END

    except CustomUser.DoesNotExist:
        logger.error(f"❌ Ошибка: сотрудник с Telegram ID {telegram_id} не найден.")
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"❌ Ошибка в handle_staff_my_orders: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
        return ConversationHandler.END

# ======= Просмотр деталей заказа =======
async def handle_staff_order_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    telegram_id = update.effective_user.id
    callback_data = query.data

    parts = callback_data.split(":")
    if len(parts) != 2 or parts[0] != "staff_order_details":
        logger.warning(f"❌ Некорректный callback_data: {callback_data}")
        return

    order_id = int(parts[1])

    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id, is_staff=True)
        order = await sync_to_async(Order.objects.select_related("user").get)(
            id=order_id, executor_id=user.id, status="processing"
        )
        order_items = await sync_to_async(lambda: list(order.items.select_related("product").all()))()

        details = (
            f"📦 <b>Заказ #{order.id}</b>\n"
            f"👤 <b>Заказчик:</b> {order.user.first_name} {order.user.last_name}\n"
            f"📞 <b>Телефон:</b> {order.user.phone_number}\n"
            f"💰 <b>Сумма:</b> {order.total_price:.2f} ₽\n"
            f"📍 <b>Адрес:</b> {order.address or 'Не указан'}\n"
            f"📌 <b>Статус:</b> В процессе\n\n"
            f"🛍 <b>Товары:</b>\n"
        )

        for item in order_items:
            details += f"🔹 {item.product.name} — {item.quantity} шт. по {item.price:.2f} ₽\n"

        # Создаем кнопки "Завершить" и "Отменить"
        keyboard = [
            [InlineKeyboardButton("✔️ Завершить Заказ", callback_data=f"staff_complete_order:{order.id}")],
            [InlineKeyboardButton("❌ Отменить Заказ", callback_data=f"staff_cancel_order:{order.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(details, parse_mode="HTML", reply_markup=reply_markup)

    except Order.DoesNotExist:
        await query.edit_message_text("❌ Заказ не найден или уже закрыт.")
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_staff_order_details: {e}")
        await query.edit_message_text("❌ Произошла ошибка. Попробуйте позже.")



# ======= Завершение заказа =======
async def complete_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Завершение заказа по inline-кнопке "Завершить".
    """
    query = update.callback_query
    await query.answer()
    callback_data = query.data

    parts = callback_data.split(":")
    if len(parts) != 2 or parts[0] != "staff_complete_order":
        logger.warning(f"❌ Некорректный callback_data: {callback_data}")
        return

    order_id = int(parts[1])
    telegram_id = update.effective_user.id

    try:
        # Проверяем, является ли пользователь исполнителем заказа
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id, is_staff=True)
        order = await sync_to_async(Order.objects.get)(id=order_id, executor_id=user.id, status="processing")

        # Обновляем статус заказа
        order.status = "delivered"
        await sync_to_async(order.save)()

        await query.edit_message_text(f"✅ Заказ #{order.id} успешно завершён.")

        logger.info(f"✅ Заказ #{order.id} завершён пользователем {telegram_id}.")

    except Order.DoesNotExist:
        logger.error(f"❌ Ошибка: заказ #{order_id} не найден или уже завершён.")
        await query.edit_message_text("❌ Заказ не найден или уже завершён.")

    except CustomUser.DoesNotExist:
        logger.error(f"❌ Ошибка: пользователь {telegram_id} не найден или не является сотрудником.")
        await query.edit_message_text("❌ У вас нет прав для выполнения этого действия.")

    except Exception as e:
        logger.error(f"❌ Ошибка в complete_order_callback: {e}")
        await query.edit_message_text("❌ Произошла ошибка. Попробуйте позже.")


# ======= Отмена заказа =======
async def cancel_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отмена заказа по inline-кнопке.
    """
    query = update.callback_query
    await query.answer()
    callback_data = query.data

    parts = callback_data.split(":")
    if len(parts) != 2 or parts[0] != "staff_cancel_order":
        logger.warning(f"❌ Некорректный callback_data: {callback_data}")
        return

    order_id = int(parts[1])

    try:
        order = await sync_to_async(Order.objects.get)(id=order_id, status="processing")
        order.status = "canceled"
        await sync_to_async(order.save)()
        await query.edit_message_text(f"❌ Заказ #{order.id} был отменён.")

        logger.info(f"✅ Заказ #{order.id} отменён пользователем {update.effective_user.id}.")

    except Order.DoesNotExist:
        logger.error(f"❌ Заказ с ID {order_id} не найден или уже отменён.")
        await query.edit_message_text("⚠️ Заказ не найден или уже отменён.")



# ======= Уведомления =======
async def async_send_new_order_notification(order):
    """
    Отправка уведомлений о новом заказе сотрудникам.
    """
    try:
        staff_users = await sync_to_async(
            lambda: list(CustomUser.objects.filter(is_staff=True, telegram_id__isnull=False))
        )()

        order_items = await sync_to_async(lambda: list(order.items.prefetch_related("product").all()))()
        phone_number = order.user.phone_number if order.user.phone_number else "Не указан"

        order_message = (
            f"📦 **Новый заказ #{order.id}**\n"
            f"🌸 Состав заказа:\n"
            + "\n".join(
                [f"- {item.product.name}: {item.quantity} шт. по {item.price:.2f} руб." for item in order_items]
            )
            + f"\n💰 Общая сумма: {order.total_price:.2f} руб.\n"
            f"📍 Адрес доставки: {order.address or 'Не указан'}\n"
            f"📞 Телефон клиента: {phone_number}"
        )

        keyboard = [[InlineKeyboardButton("Взять в работу", callback_data=f"take_order_{order.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ValueError("Токен Telegram бота отсутствует. Проверьте файл .env.")

        app = Application.builder().token(token).build()
        await app.initialize()

        for staff in staff_users:
            await app.bot.send_message(
                chat_id=staff.telegram_id,
                text=order_message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )

        await app.shutdown()
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомлений: {e}", exc_info=True)


def send_new_order_notification(order):
    """
    Синхронная обертка для отправки уведомлений о заказах.
    """
    asyncio.run(async_send_new_order_notification(order))









# ======= Взятие заказа в работу =======
async def take_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик для кнопки "Взять в работу".
    """
    query = update.callback_query
    await query.answer()
    callback_data = query.data

    if callback_data.startswith("take_order_"):
        order_id = int(callback_data.split("_")[2])
        try:
            order = await sync_to_async(Order.objects.get)(id=order_id, status="created")
            order.status = "processing"
            await sync_to_async(order.save)()
            await query.edit_message_text(f"✅ Заказ #{order.id} взят в работу.")
        except Order.DoesNotExist:
            await query.edit_message_text("❌ Этот заказ больше не существует.")

# ======= Обновление статуса заказа =======
async def update_order_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обновление статуса заказа по inline-кнопке.
    """
    query = update.callback_query
    await query.answer()
    try:
        _, order_id, new_status = query.data.split("_")
        if new_status not in ["processing", "delivered", "canceled"]:
            raise ValueError("Недопустимый статус заказа.")
        order = await sync_to_async(Order.objects.get)(id=order_id)
        order.status = new_status
        await sync_to_async(order.save)()
        await query.edit_message_text(f"✅ Статус заказа #{order.id} успешно изменён на '{new_status}'.")
    except ValueError as e:
        await query.edit_message_text(f"Ошибка: {e}")
    except Exception as e:
        logger.error(f"Ошибка при изменении статуса заказа: {e}", exc_info=True)
        await query.edit_message_text("Произошла ошибка при изменении статуса заказа.")



# ======= Обработчик команды 'ℹ️ Помощь' =======
async def handle_staff_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик текстовой команды 'ℹ️ Помощь' для сотрудников.
    """
    await update.message.reply_text(
        "🛠️ **Помощь для сотрудников:**\n\n"
        "📦 **Новые заказы** — посмотреть доступные заказы, которые можно взять в работу.\n"
        "🔄 **Текущие заказы** — список заказов, которые вы выполняете.\n"
        "❓ **Помощь** — описание доступных команд.",
        parse_mode="HTML"
    )


