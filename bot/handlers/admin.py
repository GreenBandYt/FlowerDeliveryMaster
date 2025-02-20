# bot/handlers/admin.py

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from datetime import datetime, timedelta  # Для аналитики
from bot.keyboards.admin_keyboards import admin_keyboard
from bot.utils.callback_parser import parse_callback_data
from users.models import CustomUser
from catalog.models import Order
from prettytable import PrettyTable

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ======= Обработчик команды /start =======
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE, user: CustomUser):

    """
    Приветствие администратора.
    """
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=update.effective_user.id)
        await update.message.reply_text(
            f"👑 Здравствуйте, {user.username} (Администратор)!\n"
            "💻 Доступные команды:\n"
            "📊 Аналитика\n"
            "👥 Управление пользователями\n"
            "📦 Управление заказами\n"
            "ℹ️ Помощь",
            reply_markup=admin_keyboard,
        )
    except CustomUser.DoesNotExist:
        logger.error(f"Пользователь с Telegram ID {update.effective_user.id} не найден.")
        await update.message.reply_text("Ваш аккаунт не зарегистрирован в системе.")
    except Exception as e:
        logger.error(f"Ошибка в admin_start: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")


# ======= Обработчик команды 'ℹ️ Помощь' =======
async def handle_admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик текстовой команды 'ℹ️ Помощь' для администратора.
    """
    await update.message.reply_text(
        "👑 **Помощь для администратора:**\n\n"
        "📊 Аналитика\n"
        "👥 Управление пользователями\n"
        "📦 Управление заказами\n"
        "ℹ️ Помощь"
    )
# ======= Обработчик текстовой команды '📦 Заказы' =======
async def handle_admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик текстовой команды '📦 Заказы'.
    Просмотр всех заказов.
    """
    try:
        all_orders = await sync_to_async(lambda: list(Order.objects.select_related("user").all()))()
        if not all_orders:
            await update.message.reply_text("Заказов пока нет.")
            return

        table = PrettyTable(["ID", "Дата", "Статус", "Сумма", "Клиент"])
        for order in all_orders:
            table.add_row([
                order.id,
                order.created_at.strftime("%Y-%m-%d %H:%M"),
                order.get_status_display(),
                f"{order.total_price:.2f} руб." if order.total_price else "0.00 руб.",
                order.user.username if order.user else "Не указан",
            ])

        table_str = table.get_string()
        MAX_MESSAGE_LENGTH = 4000
        lines = table_str.split("\n")
        chunk = ""
        for line in lines:
            if len(chunk) + len(line) + 1 > MAX_MESSAGE_LENGTH:
                await update.message.reply_text(f"<pre>{chunk}</pre>", parse_mode="HTML")
                chunk = line + "\n"
            else:
                chunk += line + "\n"

        if chunk:
            await update.message.reply_text(f"<pre>{chunk}</pre>", parse_mode="HTML")

    except Exception as e:
        logger.error(f"Ошибка в handle_admin_orders: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")


# ======= Обработчик деталей заказа =======
async def handle_order_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик для отображения деталей заказа.
    """
    try:
        order_id = int(update.message.text)
        order = await sync_to_async(Order.objects.select_related("user").get)(id=order_id)

        order_info = (
            f"📦 **Детали заказа #{order.id}**\n"
            f"📅 Дата: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"📌 Статус: {order.get_status_display()}\n"
            f"💰 Сумма: {order.total_price:.2f} руб.\n"
            f"👤 Клиент: {order.user.username if order.user else 'Не указан'}"
        )

        keyboard = [
            [
                InlineKeyboardButton("Новый", callback_data=f"order_status_update:{order.id}:new"),
                InlineKeyboardButton("В процессе", callback_data=f"order_status_update:{order.id}:processing"),
                InlineKeyboardButton("Завершён", callback_data=f"order_status_update:{order.id}:completed"),
            ],
            [InlineKeyboardButton("Отмена", callback_data="cancel_order_status")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(order_info, parse_mode="Markdown", reply_markup=reply_markup)

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректный номер заказа.")
    except Order.DoesNotExist:
        await update.message.reply_text("Заказ с таким номером не найден.")
    except Exception as e:
        logger.error(f"Ошибка в handle_order_details: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка при загрузке деталей заказа.")

# ======= Обработчик команды '👥 Пользователи' =======
async def handle_admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик текстовой команды '👥 Пользователи' для просмотра и управления статусами пользователей.
    """
    try:
        users = await sync_to_async(lambda: list(CustomUser.objects.filter(is_superuser=False)))()
        if not users:
            await update.message.reply_text("Пользователи не найдены.")
            return

        table = PrettyTable(["ID", "Имя", "Email", "Статус"])
        for user in users:
            status = "Сотрудник" if user.is_staff else "Клиент"
            table.add_row([user.id, user.username, user.email, status])

        table_str = table.get_string()
        await update.message.reply_text(
            f"Список сотрудников и клиентов:\n```\n{table_str}\n```",
            parse_mode="Markdown",
        )
        await update.message.reply_text("Введите ID пользователя для изменения его статуса:")

        context.user_data["state"] = "AWAIT_USER_ID"

    except Exception as e:
        logger.error(f"Ошибка в handle_admin_users: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")


# ======= Обработчик изменения статуса пользователя =======
async def handle_user_status_update_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик ввода ID пользователя для изменения его статуса.
    """
    try:
        if context.user_data.get("state") != "AWAIT_USER_ID":
            await update.message.reply_text("Вы не в режиме изменения статусов. Начните заново.")
            return

        entered_user_id = int(update.message.text.strip())
        user = await sync_to_async(CustomUser.objects.get)(id=entered_user_id, is_superuser=False)

        status = "Сотрудник" if user.is_staff else "Клиент"
        user_info = (
            f"👤 **Пользователь #{user.id}**\n"
            f"Имя: {user.username}\n"
            f"Email: {user.email}\n"
            f"Текущий статус: {status}"
        )

        keyboard = [
            [
                InlineKeyboardButton("Сделать сотрудником", callback_data=f"user_status_update:{user.id}:true"),
                InlineKeyboardButton("Сделать клиентом", callback_data=f"user_status_update:{user.id}:false"),
            ],
            [InlineKeyboardButton("Отмена", callback_data="cancel_user_status")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(user_info, parse_mode="Markdown", reply_markup=reply_markup)

        context.user_data["state"] = None

    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректный ID пользователя.")
    except CustomUser.DoesNotExist:
        await update.message.reply_text("Пользователь с таким ID не найден.")
    except Exception as e:
        logger.error(f"Ошибка в handle_user_status_update_request: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")


# ======= Callback для обновления статуса пользователя =======
async def update_user_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик inline-кнопок для изменения статуса пользователя.
    """
    query = update.callback_query
    await query.answer()

    try:
        action, params = parse_callback_data(query.data)
        if action == "cancel_user_status":
            await query.edit_message_text("⚠️ Действие отменено.")
            return

        user_id, is_staff = params
        user = await sync_to_async(CustomUser.objects.get)(id=user_id)

        user.is_staff = is_staff.lower() == "true"
        await sync_to_async(user.save)()

        new_status = "Сотрудник" if user.is_staff else "Клиент"
        await query.edit_message_text(f"✅ Статус пользователя #{user.id} изменён на '{new_status}'.")
        logger.info(f"Статус пользователя #{user.id} изменён на '{new_status}'.")

    except Exception as e:
        logger.error(f"Ошибка в update_user_status_callback: {e}", exc_info=True)
        await query.edit_message_text("Произошла ошибка при изменении статуса.")

# ======= Кнопки для аналитики =======
def get_analytics_buttons():
    keyboard = [
        [InlineKeyboardButton("Сегодня", callback_data="analytics_today")],
        [InlineKeyboardButton("Последние 7 дней", callback_data="analytics_week")],
        [InlineKeyboardButton("Текущий месяц", callback_data="analytics_month")],
        [InlineKeyboardButton("Текущий год", callback_data="analytics_year")],
        [InlineKeyboardButton("Всё время", callback_data="analytics_all_time")],
        [InlineKeyboardButton("Отмена", callback_data="analytics_cancel")],
    ]
    return InlineKeyboardMarkup(keyboard)



# ======= Точка входа в аналитику =======
async def handle_admin_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Точка входа в аналитику. Отправляет инлайн-кнопки для выбора периода.
    """
    await update.message.reply_text(
        text="📊 **Аналитика:**\n\nВыберите период:",
        reply_markup=get_analytics_buttons(),
        parse_mode="Markdown",
    )

async def analytics_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает запрос аналитики за сегодня.
    """
    query = update.callback_query
    await query.answer()

    try:
        filter_kwargs = {"created_at__date": datetime.now().date()}
        analytics_text = await get_analytics_text("Сегодня", filter_kwargs)
        await query.edit_message_text(analytics_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка в analytics_today: {e}", exc_info=True)
        await query.edit_message_text("❌ Ошибка при загрузке аналитики.")


async def analytics_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает запрос аналитики за последние 7 дней.
    """
    query = update.callback_query
    await query.answer()

    try:
        filter_kwargs = {"created_at__gte": datetime.now().date() - timedelta(days=7)}
        analytics_text = await get_analytics_text("Последние 7 дней", filter_kwargs)
        await query.edit_message_text(analytics_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка в analytics_week: {e}", exc_info=True)
        await query.edit_message_text("❌ Ошибка при загрузке аналитики.")


async def analytics_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает запрос аналитики за текущий месяц.
    """
    query = update.callback_query
    await query.answer()

    try:
        filter_kwargs = {
            "created_at__month": datetime.now().month,
            "created_at__year": datetime.now().year,
        }
        analytics_text = await get_analytics_text("Текущий месяц", filter_kwargs)
        await query.edit_message_text(analytics_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка в analytics_month: {e}", exc_info=True)
        await query.edit_message_text("❌ Ошибка при загрузке аналитики.")


async def analytics_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает запрос аналитики за текущий год.
    """
    query = update.callback_query
    await query.answer()

    try:
        filter_kwargs = {"created_at__year": datetime.now().year}
        analytics_text = await get_analytics_text("Текущий год", filter_kwargs)
        await query.edit_message_text(analytics_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка в analytics_year: {e}", exc_info=True)
        await query.edit_message_text("❌ Ошибка при загрузке аналитики.")


async def analytics_all_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает запрос аналитики за всё время.
    """
    query = update.callback_query
    await query.answer()

    try:
        filter_kwargs = {}  # Все заказы без ограничений по времени
        analytics_text = await get_analytics_text("Всё время", filter_kwargs)
        await query.edit_message_text(analytics_text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка в analytics_all_time: {e}", exc_info=True)
        await query.edit_message_text("❌ Ошибка при загрузке аналитики.")


async def analytics_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отмена запроса аналитики.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔙 Вы вышли из аналитики.")


async def get_analytics_text(title: str, filter_kwargs: dict) -> str:
    """
    Формирует текст аналитики по заданным фильтрам.
    """
    total_orders = await sync_to_async(lambda: Order.objects.filter(**filter_kwargs).count())()
    total_revenue = await sync_to_async(
        lambda: sum(order.total_price for order in Order.objects.filter(**filter_kwargs))
    )()
    average_order_value = total_revenue / total_orders if total_orders > 0 else 0
    total_users = await sync_to_async(lambda: CustomUser.objects.count())()

    analytics_text = (
        f"📊 **Аналитика за {title}:**\n\n"
        f"👤 Пользователи: **{total_users}**\n"
        f"📦 Всего заказов: **{total_orders}**\n"
        f"💰 Общий доход: **{total_revenue:.2f} ₽**\n"
        f"🧾 Средний чек: **{average_order_value:.2f} ₽**"
    )
    return analytics_text




#
# # ======= Обработчик выбора периода аналитики =======
# async def analytics_period_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Обрабатывает выбор периода аналитики и отправляет данные.
#     """
#     query = update.callback_query
#     await query.answer()
#
#     try:
#         action, params = parse_callback_data(query.data)
#         if action != "analytics_period":
#             await query.edit_message_text("Неверный формат данных.")
#             return
#
#         period = params[0]
#         title = ""
#         filter_kwargs = {}
#
#         if period == "today":
#             filter_kwargs = {"created_at__date": datetime.now().date()}
#             title = "Сегодня"
#         elif period == "week":
#             filter_kwargs = {"created_at__gte": datetime.now().date() - timedelta(days=7)}
#             title = "Последние 7 дней"
#         elif period == "month":
#             filter_kwargs = {
#                 "created_at__month": datetime.now().month,
#                 "created_at__year": datetime.now().year,
#             }
#             title = "Текущий месяц"
#         elif period == "year":
#             filter_kwargs = {"created_at__year": datetime.now().year}
#             title = "Текущий год"
#         elif period == "all":
#             filter_kwargs = {}
#             title = "Всё время"
#         elif period == "cancel":
#             await query.edit_message_text("🔙 Вы вышли из аналитики.")
#             return
#
#         # Получение данных аналитики
#         total_orders = await sync_to_async(lambda: Order.objects.filter(**filter_kwargs).count())()
#         total_revenue = await sync_to_async(
#             lambda: sum(order.total_price for order in Order.objects.filter(**filter_kwargs))
#         )()
#         average_order_value = total_revenue / total_orders if total_orders > 0 else 0
#         total_users = await sync_to_async(lambda: CustomUser.objects.count())()
#
#         analytics_text = (
#             f"📊 **Аналитика за {title}:**\n\n"
#             f"👤 Пользователи: **{total_users}**\n"
#             f"📦 Всего заказов: **{total_orders}**\n"
#             f"💰 Общий доход: **{total_revenue:.2f} ₽**\n"
#             f"🧾 Средний чек: **{average_order_value:.2f} ₽**"
#         )
#         await query.edit_message_text(analytics_text, parse_mode="Markdown")
#
#     except Exception as e:
#         logger.error(f"Ошибка в analytics_period_handler: {e}", exc_info=True)
#         await query.edit_message_text("Произошла ошибка при обработке аналитики.")
