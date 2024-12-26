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

# Настройка логгера
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
AWAIT_ORDER_ID = 1
AWAIT_NEW_STATUS = 2

async def staff_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Приветствие сотрудника.
    """
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=update.effective_user.id)
    await update.message.reply_text(
        f"🛠️ Здравствуйте, {user.username} (Сотрудник)!\n"
        "🔧 Доступные команды:\n"
        "📦 /my_orders - Текущие заказы\n"
        "🔄 /update_status - Обновление статуса заказов\n"
        "ℹ️ /look_help - Помощь посмотреть",
        reply_markup=staff_keyboard
    )

async def look_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /look_help для сотрудника.
    """
    await update.message.reply_text(
        "🛠️ Помощь для сотрудников:\n"
        "📦 /my_orders - Текущие заказы\n"
        "🔄 /update_status - Обновление статуса заказов\n"
        "ℹ️ /look_help - Помощь посмотреть"
    )


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


# ======= Просмотр заказов =======
async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Отображение текущих заказов сотрудника.
    """
    telegram_id = update.effective_user.id
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id, is_staff=True)
        orders = await sync_to_async(lambda: list(Order.objects.filter(status="processing")))()

        if not orders:
            await update.message.reply_text("❌ У вас нет активных заказов в работе.")
            return ConversationHandler.END

        # Формируем сообщение с заказами
        message = "📋 <b>Текущие заказы:</b>\n\n"
        for order in orders:
            message += (
                f"📦 Заказ #{order.id}\n"
                f"💰 Сумма: {order.total_price:.2f} ₽\n"
                f"📍 Адрес: {order.address or 'Не указан'}\n"
                f"📌 Статус: {order.status}\n\n"
            )
        await update.message.reply_text(message, parse_mode="HTML")
        return AWAIT_ORDER_ID
    except CustomUser.DoesNotExist:
        logger.error(f"Сотрудник с Telegram ID {telegram_id} не найден.")
        await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
        return ConversationHandler.END


# ======= Детали заказа =======
async def order_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Отображение деталей выбранного заказа.
    """
    try:
        order_id = int(update.message.text)
        order = await sync_to_async(Order.objects.get)(id=order_id, status="processing")

        # Формируем сообщение с деталями заказа
        details = (
            f"📦 <b>Детали заказа #{order.id}:</b>\n"
            f"💰 Сумма: {order.total_price} ₽\n"
            f"📍 Адрес: {order.address or 'Не указан'}\n"
            f"📌 Статус: {order.status}\n"
        )
        keyboard = [
            [InlineKeyboardButton("✅ Взять в работу", callback_data=f"take_order_{order.id}")],
            [InlineKeyboardButton("✔️ Завершить", callback_data=f"complete_order_{order.id}")],
            [InlineKeyboardButton("❌ Отказаться", callback_data=f"cancel_order_{order.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(details, parse_mode="HTML", reply_markup=reply_markup)
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("⚠️ Введите корректный ID заказа.")
        return AWAIT_ORDER_ID
    except Order.DoesNotExist:
        await update.message.reply_text("⚠️ Заказ с таким ID не найден.")
        return AWAIT_ORDER_ID



# ======= Завершение заказа =======
async def complete_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Завершение заказа по inline-кнопке.
    """
    query = update.callback_query
    await query.answer()
    callback_data = query.data

    if callback_data.startswith("complete_order_"):
        order_id = callback_data.replace("complete_order_", "")
        try:
            order = await sync_to_async(Order.objects.get)(id=order_id, status="processing")
            order.status = "completed"
            await sync_to_async(order.save)()
            await query.edit_message_text(f"✅ Заказ #{order.id} успешно завершён.")
        except Order.DoesNotExist:
            logger.error(f"Заказ с ID {order_id} не найден или уже завершён.")
            await query.edit_message_text("❌ Заказ не найден или уже завершён.")


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
        if new_status not in ["processing", "completed", "canceled"]:
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


# ======= Меню для сотрудников =======
async def handle_staff_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📦 Мои заказы":
        await my_orders(update, context)
    elif text == "🔄 Обновить статус":
        await update.message.reply_text("Для обновления статуса выберите заказ.")
    elif text == "ℹ️ Помощь":
        await update.message.reply_text("Обратитесь к администратору для получения помощи.")
    else:
        await update.message.reply_text("❓ Команда не распознана. Используйте меню.", reply_markup=staff_keyboard)
