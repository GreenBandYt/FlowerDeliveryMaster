# bot/handlers/admin.py

import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler, ConversationHandler, CallbackContext
from asgiref.sync import sync_to_async
from users.models import CustomUser
from catalog.models import Order
from prettytable import PrettyTable
from datetime import datetime, timedelta  # Для аналитики
from bot.keyboards.admin_keyboards import admin_keyboard
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
AWAIT_USER_ID = 1
CHOOSE_PERIOD, EXIT_ANALYTICS = range(2)


async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Приветствие администратора.
    """
    user = await sync_to_async(CustomUser.objects.get)(telegram_id=update.effective_user.id)
    await update.message.reply_text(
        f"👑 Здравствуйте, {user.username} (Администратор)!\n"
        "💻 Доступные команды:\n"
        "📊 /analytics - Просмотр аналитики\n"
        "👥 /manage_users - Пользователи\n"
        "📦 /orders - Управление заказами\n"
        "ℹ️ /admin_help - Помощь",
        reply_markup=admin_keyboard
    )

# ======= Помощь для администратора =======
async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /admin_help для вывода списка доступных администратору команд.
    """
    await update.message.reply_text(
        "👑 **Помощь для администратора:**\n\n"
        "📊 /analytics - Аналитика\n"
        "👥 /manage_users - Пользователи\n"
        "📦 /orders - Заказы\n"
        "ℹ️ /admin_help - Помощь",
        parse_mode="Markdown"
    )

# Обработчик команды /orders
AWAIT_ORDER_ID = 1


# ======= Управление заказами: Просмотр всех заказов =======
async def orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id)
        if not (user.is_superuser or user.is_staff):
            await update.message.reply_text("У вас нет доступа к этой команде.")
            return ConversationHandler.END

        all_orders = await sync_to_async(lambda: list(Order.objects.select_related('user').all()))()
        if not all_orders:
            await update.message.reply_text("Заказов пока нет.")
            return ConversationHandler.END

        table = PrettyTable(["ID", "Дата", "Статус", "Сумма", "Клиент"])
        for order in all_orders:
            table.add_row([
                order.id,
                order.created_at.strftime("%Y-%m-%d %H:%M"),
                order.get_status_display(),
                f"{order.total_price:.2f} руб." if order.total_price else "0.00 руб.",
                order.user.username if order.user else "Не указан"
            ])

        # Разбиваем таблицу на части
        table_str = table.get_string()
        MAX_MESSAGE_LENGTH = 4000  # Максимальная длина сообщения с запасом

        # Разделяем сообщение по строкам
        lines = table_str.split("\n")
        chunk = ""
        for line in lines:
            if len(chunk) + len(line) + 1 > MAX_MESSAGE_LENGTH:
                await update.message.reply_text(f"<pre>{chunk}</pre>", parse_mode="HTML")
                chunk = line + "\n"
            else:
                chunk += line + "\n"

        # Отправка последнего чанка
        if chunk:
            await update.message.reply_text(f"<pre>{chunk}</pre>", parse_mode="HTML")

    except CustomUser.DoesNotExist:
        await update.message.reply_text("Ваш аккаунт не зарегистрирован в системе.")
    except Exception as e:
        logger.error(f"Ошибка в обработке команды /orders: {e}", exc_info=True)
        await update.message.reply_text(f"Произошла ошибка: {e}")

# ======= Управление заказами: Подробности заказа =======

async def order_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик ввода ID заказа.
    Показывает подробности выбранного заказа и добавляет кнопки для смены статуса, включая "Отмена".
    """
    try:
        # Получаем ID заказа из сообщения пользователя
        order_id = int(update.message.text)
        order = await sync_to_async(Order.objects.select_related('user').get)(id=order_id)

        # Формируем сообщение с деталями заказа
        order_info = (
            f"📦 **Детали заказа #{order.id}**\n"
            f"📅 Дата: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"📌 Статус: {order.get_status_display()}\n"
            f"💰 Сумма: {order.total_price:.2f} руб.\n"
            f"👤 Клиент: {order.user.username if order.user else 'Не указан'}"
        )

        # Добавляем кнопки для смены статуса и "Отмена"
        keyboard = [
            [InlineKeyboardButton("Новый", callback_data=f"status_{order.id}_new")],
            [InlineKeyboardButton("В процессе", callback_data=f"status_{order.id}_processing")],
            [InlineKeyboardButton("Завершён", callback_data=f"status_{order.id}_completed")],
            [InlineKeyboardButton("Отмена", callback_data=f"cancel_order_status_{order.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем сообщение с кнопками
        await update.message.reply_text(order_info, parse_mode="Markdown", reply_markup=reply_markup)
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректный номер заказа.")
        return AWAIT_ORDER_ID
    except Order.DoesNotExist:
        await update.message.reply_text("Заказ с таким номером не найден. Попробуйте снова.")
        return AWAIT_ORDER_ID
    except Exception as e:
        logger.error(f"Ошибка при загрузке деталей заказа: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка при загрузке деталей заказа.")
        return ConversationHandler.END

# ======= Управление заказами: Обновление статуса заказа =======
async def update_order_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик inline-кнопок для смены статуса заказа.
    """
    query = update.callback_query
    await query.answer()

    try:
        # Получаем данные из callback (формат: "status_<order_id>_<new_status>" или "cancel_order_status_<order_id>")
        callback_data = query.data
        if callback_data.startswith("cancel_order_status_"):
            # Обработка нажатия "Отмена"
            await query.delete_message()  # Удаляем сообщение с кнопками
            return

        # Извлекаем ID заказа и новый статус
        _, order_id, new_status = callback_data.split("_")
        order = await sync_to_async(Order.objects.get)(id=order_id)

        # Обновляем статус заказа
        order.status = new_status
        await sync_to_async(order.save)()

        await query.edit_message_text(f"✅ Статус заказа #{order.id} успешно изменён на '{new_status}'.")
    except Exception as e:
        logger.error(f"Ошибка при изменении статуса заказа: {e}", exc_info=True)
        await query.edit_message_text("Произошла ошибка при изменении статуса заказа.")




# ======= Управление пользователями =======
async def manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Команда /manage_users для управления пользователями.
    """
    telegram_id = update.effective_user.id
    try:
        admin = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id)
        if not admin.is_superuser:
            await update.message.reply_text("У вас нет доступа к этой команде.")
            return ConversationHandler.END

        users = await sync_to_async(lambda: list(CustomUser.objects.filter(is_superuser=False)))()
        if not users:
            await update.message.reply_text("Пользователи не найдены.")
            return ConversationHandler.END

        table = PrettyTable(["ID", "Имя", "Email", "Статус"])
        for user in users:
            status = "Сотрудник" if user.is_staff else "Клиент"
            table.add_row([user.id, user.username, user.email, status])

        table_str = table.get_string()
        await update.message.reply_text(
            f"Список сотрудников и клиентов:\n```\n{table_str}\n```",
            parse_mode="Markdown"
        )
        await update.message.reply_text("Введите ID пользователя для изменения его статуса:")
        return AWAIT_USER_ID
    except CustomUser.DoesNotExist:
        await update.message.reply_text("Ваш аккаунт не зарегистрирован как администратор.")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Ошибка в /manage_users: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка.")
        return ConversationHandler.END

# ======= Обновление статуса пользователя =======
async def update_user_is_staff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик для ввода ID пользователя.
    Отображает кнопки для смены статуса (Сотрудник/Клиент).
    """
    text = update.message.text.strip()

    # Проверяем, не вводит ли пользователь команду "Отмена"
    if text.lower() == "/cancel" or text.lower() == "отмена":
        await update.message.reply_text("Вы вышли из режима изменения статуса пользователей.")
        return ConversationHandler.END

    try:
        # Получаем ID пользователя из сообщения
        user_id = int(text)
        user = await sync_to_async(CustomUser.objects.get)(id=user_id, is_superuser=False)

        # Формируем сообщение с информацией о пользователе
        status = "Сотрудник" if user.is_staff else "Клиент"
        user_info = (
            f"👤 **Пользователь #{user.id}**\n"
            f"Имя: {user.username}\n"
            f"Email: {user.email}\n"
            f"Текущий статус: {status}"
        )

        # Кнопки для изменения статуса и отмены
        keyboard = [
            [InlineKeyboardButton("Сделать сотрудником", callback_data=f"staff_{user.id}_true")],
            [InlineKeyboardButton("Сделать клиентом", callback_data=f"staff_{user.id}_false")],
            [InlineKeyboardButton("Отмена", callback_data=f"cancel_user_status_{user.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем сообщение с кнопками
        await update.message.reply_text(user_info, parse_mode="Markdown", reply_markup=reply_markup)
        return AWAIT_USER_ID

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректный ID пользователя.")
        return AWAIT_USER_ID
    except CustomUser.DoesNotExist:
        await update.message.reply_text("Пользователь не найден или является администратором.")
        return AWAIT_USER_ID
    except Exception as e:
        logger.error(f"Ошибка в update_user_is_staff: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка.")
        return ConversationHandler.END


async def cancel_manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Выход из режима управления пользователями.
    """
    await update.message.reply_text("Вы вышли из режима управления пользователями.")
    return ConversationHandler.END  # Завершение сессии


# Callback-обработчик для отмены или смены статуса пользователя
async def update_user_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        logger.info(f"Callback data received: {query.data}")

        # Если нажата кнопка "Отмена"
        if query.data.startswith("cancel_user_status_"):
            await query.edit_message_text("⚠️ Действие отменено. Вы вышли из режима изменения статуса пользователя.")
            return ConversationHandler.END  # Завершаем процесс корректно

        # Обработка изменения статуса
        _, user_id, is_staff = query.data.split("_")
        user = await sync_to_async(CustomUser.objects.get)(id=user_id)

        # Обновляем статус пользователя
        user.is_staff = is_staff == "true"
        await sync_to_async(user.save)()

        new_status = "Сотрудник" if user.is_staff else "Клиент"
        await query.edit_message_text(f"✅ Статус пользователя #{user.id} изменён на '{new_status}'.")
        return ConversationHandler.END  # Завершаем процесс
    except Exception as e:
        logger.error(f"Ошибка при изменении статуса пользователя: {e}", exc_info=True)
        await query.edit_message_text("Произошла ошибка при изменении статуса.")
        return ConversationHandler.END



# ======= Обработчик для аналитики (ConversationHandler) =======
def get_analytics_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("analytics", analytics)],
        states={
            CHOOSE_PERIOD: [CallbackQueryHandler(analytics_period_handler)],
        },
        fallbacks=[CallbackQueryHandler(analytics_period_handler)],
    )

# Создание кнопок для выбора периода аналитики
def get_analytics_buttons():
    keyboard = [
        [InlineKeyboardButton("Сегодня", callback_data="analytics_today")],
        [InlineKeyboardButton("Последние 7 дней", callback_data="analytics_week")],
        [InlineKeyboardButton("Текущий месяц", callback_data="analytics_month")],
        [InlineKeyboardButton("Текущий год", callback_data="analytics_year")],
        [InlineKeyboardButton("Всё время", callback_data="analytics_all")],
        [InlineKeyboardButton("Отмена", callback_data="analytics_cancel")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ======= Команда аналитики /analytics =======

async def analytics(update: Update, context: CallbackContext) -> int:
    """
    Начало аналитики: отправляем кнопки для выбора периода.
    """
    await update.message.reply_text(
        text=f"📊 **Аналитика:**\n\nВыберите период:",
        reply_markup=get_analytics_buttons(),
        parse_mode="Markdown"
    )
    return CHOOSE_PERIOD

# ======= Обработчик выбора периода аналитики =======

async def analytics_period_handler(update: Update, context: CallbackContext) -> int:
    """
    Обрабатывает выбор периода и отправляет данные аналитики.
    """
    query = update.callback_query
    await query.answer()

    # Определяем период на основе callback_data
    period = query.data
    if period == "analytics_cancel":
        await query.edit_message_text("🔙 Вы вышли из меню аналитики.")
        return ConversationHandler.END

    title = ""
    filter_kwargs = {}

    # Установка фильтра на период
    if period == "analytics_today":
        filter_kwargs = {"created_at__date": datetime.now().date()}
        title = "Сегодня"
    elif period == "analytics_week":
        filter_kwargs = {"created_at__gte": datetime.now().date() - timedelta(days=7)}
        title = "Последние 7 дней"
    elif period == "analytics_month":
        filter_kwargs = {
            "created_at__month": datetime.now().month,
            "created_at__year": datetime.now().year,
        }
        title = "Текущий месяц"
    elif period == "analytics_year":
        filter_kwargs = {"created_at__year": datetime.now().year}
        title = "Текущий год"
    elif period == "analytics_all":
        filter_kwargs = {}
        title = "Всё время"

    # Подсчет значений
    total_orders = await sync_to_async(lambda: Order.objects.filter(**filter_kwargs).count())()
    total_revenue = await sync_to_async(lambda: sum(order.total_price for order in Order.objects.filter(**filter_kwargs)))()
    average_order_value = total_revenue / total_orders if total_orders > 0 else 0
    total_users = await sync_to_async(lambda: CustomUser.objects.count())()

    # Формируем текст аналитики
    analytics_text = (
        f"📊 **Аналитика за {title}:**\n\n"
        f"👤 Пользователи: **{total_users}**\n"
        f"📦 Всего заказов: **{total_orders}**\n"
        f"💰 Общий доход: **{total_revenue or 0:.2f} ₽**\n"
        f"🧾 Средний чек: **{average_order_value or 0:.2f} ₽**"
    )
    await query.edit_message_text(analytics_text, parse_mode="Markdown")
    return ConversationHandler.END
