# bot/handlers/admin.py

import logging
from django.db.models import Count

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from datetime import datetime, timedelta  # Для аналитики
from bot.keyboards.admin_keyboards import admin_keyboard
from bot.utils.callback_parser import parse_callback_data
from users.models import CustomUser
from catalog.models import Order
from prettytable import PrettyTable
from bot.utils.access_control import check_access
from bot.utils.messaging import send_message


# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Словарь перевода статусов для вывода пользователям
STATUS_TRANSLATION = {
    "created": "Новый",
    "processing": "В процессе",
    "shipped": "Отправлен",
    "delivered": "Доставлен",
    "canceled": "Отменён"
}


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
    Показывает список всех заказов + кнопки выбора категории.
    """
    try:
        all_orders = await sync_to_async(lambda: list(Order.objects.select_related("user").all()))()
        if not all_orders:
            await update.message.reply_text("❌ Заказов пока нет.")
            return

        # ✅ Создаём таблицу с заказами
        table = PrettyTable(["ID", "Дата", "Статус", "Сумма", "Клиент"])
        for order in all_orders:
            translated_status = STATUS_TRANSLATION.get(order.status, "Неизвестный статус")  # Перевод статуса
            table.add_row([
                order.id,
                order.created_at.strftime("%Y-%m-%d %H:%M"),
                translated_status,
                f"{order.total_price:.2f} руб." if order.total_price else "0.00 руб.",
                order.user.username if order.user else "Не указан",
            ])

        table_str = table.get_string()
        await update.message.reply_text(f"<pre>{table_str}</pre>", parse_mode="HTML")

        # ✅ Добавляем кнопки выбора статуса
        keyboard = [
            [InlineKeyboardButton("🆕 Новые", callback_data="orders_new")],
            [InlineKeyboardButton("🔄 В процессе", callback_data="orders_processing")],
            [InlineKeyboardButton("✅ Завершённые", callback_data="orders_completed")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("📦 Выберите категорию заказов:", reply_markup=reply_markup)

    except Exception as e:
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")



# ======= Обработчик деталей заказа =======
async def handle_order_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик для отображения деталей заказа.
    Показывает информацию о заказе и кнопки для действий.
    """
    query = update.callback_query
    await query.answer()

    try:
        # Получаем ID заказа из callback_data
        order_id = int(query.data.split(":")[1])
        order = await sync_to_async(Order.objects.select_related("user").get)(id=order_id)

        # Переводим статус
        translated_status = STATUS_TRANSLATION.get(order.status, "Неизвестный статус")

        # Формируем текст с деталями заказа
        order_info = (
            f"📦 **Детали заказа #{order.id}**\n"
            f"📅 Дата: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"📌 Статус: {translated_status}\n"
            f"💰 Сумма: {order.total_price:.2f} руб.\n"
            f"👤 Клиент: {order.user.username if order.user else 'Не указан'}"
        )

        # Формируем кнопки
        keyboard = []

        # Если заказ "Новый", добавляем кнопку назначения исполнителя
        if order.status == "created":  # ✅ Исправлено с "Новый" на "created"
            keyboard.append([InlineKeyboardButton("👷 Назначить исполнителя", callback_data=f"assign_executor:{order.id}")])

        # Добавляем кнопку "Назад" для возврата в список заказов
        # keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="orders_new")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        # Редактируем сообщение с деталями заказа и кнопками
        await query.edit_message_text(order_info, parse_mode="Markdown", reply_markup=reply_markup)

        logger.info(f"📦 Отправлены детали заказа #{order.id}")

    except ValueError:
        await query.edit_message_text("❌ Ошибка: неверный формат ID заказа.")
    except Order.DoesNotExist:
        await query.edit_message_text("❌ Ошибка: заказ не найден.")
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_order_details: {e}", exc_info=True)
        await query.edit_message_text("❌ Произошла ошибка при загрузке деталей заказа.")




# ======= Обработчик кнопки "🆕 Новые" =======
async def handle_orders_by_status_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопки "🆕 Новые".
    Показывает список заказов со статусом "Новый" и кнопки для просмотра деталей.
    """
    query = update.callback_query
    await query.answer()

    try:
        # Фильтруем заказы по статусу "created" вместо "Новый"
        new_orders = await sync_to_async(lambda: list(Order.objects.filter(status="created").select_related("user")))()
        if not new_orders:
            await query.edit_message_text("❌ Нет новых заказов.")
            return

        # Создаём таблицу
        table = PrettyTable(["ID", "Дата", "Сумма", "Клиент"])
        for order in new_orders:
            table.add_row([
                order.id,
                order.created_at.strftime("%Y-%m-%d %H:%M"),
                f"{order.total_price:.2f} руб." if order.total_price else "0.00 руб.",
                order.user.username if order.user else "Не указан",
            ])

        # Разбиваем на сообщения
        table_str = table.get_string()
        await query.message.reply_text(f"📦 **Новые заказы:**\n```\n{table_str}\n```", parse_mode="Markdown")

        # Кнопки для просмотра деталей
        keyboard = [
            [InlineKeyboardButton(f"📌 Заказ #{order.id}", callback_data=f"order_details:{order.id}")]
            for order in new_orders
        ]
        # keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="admin_orders")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите заказ для просмотра:", reply_markup=reply_markup)

        logger.info(f"✅ Отправлен список новых заказов ({len(new_orders)} шт.)")

    except Exception as e:
        logger.error(f"❌ Ошибка в handle_orders_by_status_new: {e}", exc_info=True)
        await query.message.reply_text("❌ Ошибка при загрузке заказов.")





# ======= Обработчик назначения исполнителя =======
async def handle_assign_executor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопки "👷 Назначить исполнителя".
    Показывает список доступных исполнителей и предлагает выбрать одного.
    """
    query = update.callback_query
    await query.answer()

    try:
        order_id = int(query.data.split(":")[1])
        order = await sync_to_async(Order.objects.select_related("user").get)(id=order_id)

        if order.status != "created":
            await query.edit_message_text("❌ Ошибка: этот заказ нельзя редактировать.")
            return

        if order.executor:
            await query.edit_message_text(f"⚠️ Исполнитель уже назначен: {order.executor.username}.")
            return

        # Фильтр: исполнители с менее чем 3 заказами
        executors = await sync_to_async(lambda: list(
            CustomUser.objects.filter(is_staff=True).annotate(order_count=Count('executor_orders')).filter(order_count__lt=3)
        ))()

        if not executors:
            await query.edit_message_text("❌ Нет доступных исполнителей.")
            return

        keyboard = [
            [InlineKeyboardButton(f"{executor.username} (ID: {executor.id})", callback_data=f"set_executor:{order_id}:{executor.id}")]
            for executor in executors
        ]
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=f"order_details:{order_id}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("Выберите исполнителя для назначения:", reply_markup=reply_markup)

        logger.info(f"👷 Отправлен список исполнителей ({len(executors)} чел.) для заказа #{order_id}")

    except ValueError:
        await query.edit_message_text("❌ Ошибка: неверный формат ID заказа.")
    except Order.DoesNotExist:
        await query.edit_message_text("❌ Ошибка: заказ не найден.")
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_assign_executor: {e}", exc_info=True)
        await query.edit_message_text("❌ Произошла ошибка.")



# ======= Обработчик назначения исполнителя на заказ =======
async def handle_set_executor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопки выбора исполнителя.
    Назначает выбранного исполнителя на заказ.
    """
    query = update.callback_query
    await query.answer()

    try:
        _, order_id, executor_id = query.data.split(":")
        order_id, executor_id = int(order_id), int(executor_id)

        order = await sync_to_async(Order.objects.select_related("user").get)(id=order_id)
        executor = await sync_to_async(CustomUser.objects.get)(id=executor_id, is_staff=True)

        if order.executor:
            await query.edit_message_text(f"⚠️ Исполнитель уже назначен: {order.executor.username}.")
            return

        # Проверяем, что у исполнителя менее 3 заказов
        executor_orders_count = await sync_to_async(lambda: executor.executor_orders.count())()
        if executor_orders_count >= 3:
            await query.edit_message_text("❌ Ошибка: у этого исполнителя уже 3 активных заказа.")
            return

        order.executor = executor
        order.status = "processing"
        await sync_to_async(order.save)()

        await query.edit_message_text(f"✅ Исполнитель **{executor.username}** назначен на заказ #{order.id}. Статус изменён на 'В обработке'.")

        logger.info(f"✅ Исполнитель {executor.username} (ID {executor.id}) назначен на заказ #{order.id}")

        # Отправляем уведомление исполнителю
        await send_message(
            context,  # Передаём сам `context`, а не `context.application.bot`
            executor.telegram_id,
            f"📦 Вам назначен новый заказ #{order.id}. Проверьте детали в системе."
        )

    except ValueError:
        await query.edit_message_text("❌ Ошибка: неверные данные.")
    except Order.DoesNotExist:
        await query.edit_message_text("❌ Ошибка: заказ не найден.")
    except CustomUser.DoesNotExist:
        await query.edit_message_text("❌ Ошибка: исполнитель не найден.")
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_set_executor: {e}", exc_info=True)
        await query.edit_message_text("❌ Ошибка при назначении исполнителя.")




# ======= Обработчик кнопки "🔄 В процессе" =======
async def handle_orders_processing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отображает заказы со статусом 'В процессе'.
    """
    query = update.callback_query
    await query.answer()

    try:
        processing_orders = await sync_to_async(lambda: list(
            Order.objects.select_related("user").filter(status="processing")
        ))()

        if not processing_orders:
            await query.edit_message_text("🔄 Нет заказов 'В процессе'.")
            return

        table = PrettyTable(["ID", "Дата", "Сумма", "Клиент"])
        for order in processing_orders:
            table.add_row([
                order.id,
                order.created_at.strftime("%Y-%m-%d %H:%M"),
                f"{order.total_price:.2f} руб.",
                order.user.username if order.user else "Не указан",
            ])

        table_str = table.get_string()
        await query.edit_message_text(f"🔄 **Заказы в процессе:**\n```\n{table_str}\n```", parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка в handle_orders_processing: {e}", exc_info=True)
        await query.edit_message_text("❌ Ошибка при загрузке заказов.")


# ======= Обработчик кнопки "✅ Завершённые" =======
async def handle_orders_completed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отображает заказы со статусом 'Завершённые'.
    """
    query = update.callback_query
    await query.answer()

    try:
        completed_orders = await sync_to_async(lambda: list(
            Order.objects.select_related("user").filter(status="delivered")
        ))()

        if not completed_orders:
            await query.edit_message_text("✅ Нет завершённых заказов.")
            return

        table = PrettyTable(["ID", "Дата", "Сумма", "Клиент"])
        for order in completed_orders:
            table.add_row([
                order.id,
                order.created_at.strftime("%Y-%m-%d %H:%M"),
                f"{order.total_price:.2f} руб.",
                order.user.username if order.user else "Не указан",
            ])

        table_str = table.get_string()
        await query.edit_message_text(f"✅ **Завершённые заказы:**\n```\n{table_str}\n```", parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка в handle_orders_completed: {e}", exc_info=True)
        await query.edit_message_text("❌ Ошибка при загрузке заказов.")




# ======= Обработчик команды '👥 Пользователи' =======
async def handle_admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды '👥 Пользователи'.
    Показывает список пользователей и переводит бота в режим ожидания ID.
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

        context.user_data["state"] = "AWAIT_USER_ID"  # Устанавливаем состояние

    except Exception as e:
        logger.error(f"Ошибка в handle_admin_users: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")


# ======= Обработчик изменения статуса пользователя =======
async def handle_user_status_update_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик ввода ID пользователя для изменения его статуса.
    """
    try:
        entered_user_id = int(update.message.text.strip())  # Парсим ID
        logger.info(f"🔍 Введён ID пользователя: {entered_user_id}")

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

        context.user_data["state"] = None  # Сбрасываем состояние

    except ValueError:
        logger.warning("⛔ Введён некорректный ID пользователя!")
        await update.message.reply_text("❌ Пожалуйста, введите корректный ID пользователя.")
    except CustomUser.DoesNotExist:
        logger.warning(f"⚠️ Пользователь с ID {entered_user_id} не найден.")
        await update.message.reply_text("❌ Пользователь с таким ID не найден.")
    except Exception as e:
        logger.error(f"❌ Ошибка в handle_user_status_update_request: {e}", exc_info=True)
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")



# ======= Callback для обновления статуса пользователя =======
async def update_user_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик inline-кнопок для изменения статуса пользователя.
    """
    query = update.callback_query
    await query.answer()

    try:
        parts = query.data.split(":")
        if len(parts) != 3:
            logger.error(f"❌ Ошибка: некорректный формат callback_data: {query.data}")
            await query.edit_message_text("❌ Произошла ошибка при изменении статуса.")
            return

        action, user_id, is_staff_str = parts
        user_id = int(user_id)
        is_staff = is_staff_str.lower() == "true"

        user = await sync_to_async(CustomUser.objects.get)(id=user_id)

        user.is_staff = is_staff
        await sync_to_async(user.save)()

        new_status = "Сотрудник" if user.is_staff else "Клиент"
        await query.edit_message_text(f"✅ Статус пользователя #{user.id} изменён на '{new_status}'.")
        logger.info(f"✅ Статус пользователя #{user.id} изменён на '{new_status}'.")

    except Exception as e:
        logger.error(f"❌ Ошибка в update_user_status_callback: {e}", exc_info=True)
        await query.edit_message_text("❌ Произошла ошибка при изменении статуса.")


async def cancel_user_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик кнопки 'Отмена' в inline-кнопках изменения статуса пользователя.
    Отвечает пользователю и редактирует сообщение, убирая кнопки.
    """
    query = update.callback_query
    await query.answer("🚫 Действие отменено.", show_alert=True)

    try:
        # Убираем inline-клавиатуру, меняем текст на уведомление об отмене
        await query.edit_message_text("⚠️ Действие отменено. Вы можете выбрать пользователя заново.")
        logger.info(f"🚫 Отмена действия: {query.message.chat.id}")

    except Exception as e:
        logger.error(f"❌ Ошибка в cancel_user_status_callback: {e}", exc_info=True)
        await query.edit_message_text("❌ Ошибка при отмене действия.")





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
