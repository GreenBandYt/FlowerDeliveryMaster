from asgiref.sync import async_to_sync, sync_to_async
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    Application,
    CallbackQueryHandler,
    CallbackContext,
    ConversationHandler,
)
import os
import re
import asyncio
from datetime import datetime, timedelta  # Добавьте этот импорт
from django.db.models import Sum, Avg
from dotenv import load_dotenv
from users.models import CustomUser
from django.db.utils import IntegrityError
from prettytable import PrettyTable
from catalog.models import Order, OrderItem
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Состояния для регистрации
USERNAME, PASSWORD, PHONE, ADDRESS = range(4)

#
# async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     username = update.message.text
#     if username.lower() == "отмена":
#         await update.message.reply_text("Регистрация отменена.")
#         return ConversationHandler.END
#     context.user_data['username'] = username
#     await update.message.reply_text("Введите пароль:")
#     return PASSWORD
#
# async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     password = update.message.text
#     context.user_data['password'] = password
#     await update.message.reply_text("Введите ваш номер телефона:")
#     return PHONE
#
# async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     phone = update.message.text
#     context.user_data['phone'] = phone
#     phone_pattern = r'^\+7\(\d{3}\)\d{3}-\d{2}-\d{2}$'
#     if not re.match(phone_pattern, phone):
#         await update.message.reply_text(
#             "Ошибка: номер телефона должен быть в формате +7(XXX)XXX-XX-XX."
#         )
#         return PHONE
#     await update.message.reply_text("Введите ваш адрес:")
#     return ADDRESS
#
# async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     address = update.message.text
#     user_data = context.user_data
#     try:
#         user = await sync_to_async(CustomUser.objects.create_user)(
#             username=user_data['username'],
#             password=user_data['password'],
#             telegram_id=update.effective_user.id,
#             phone_number=user_data['phone'],
#             address=address,
#         )
#         await sync_to_async(user.save)()
#         await update.message.reply_text("Регистрация успешна! Теперь вы можете использовать бота.")
#     except IntegrityError:
#         await update.message.reply_text(
#             "Ошибка: такое имя пользователя уже существует. Попробуйте снова."
#         )
#     except Exception as e:
#         await update.message.reply_text(f"Произошла ошибка: {e}")
#     return ConversationHandler.END
#
# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text("Регистрация отменена.")
#     return ConversationHandler.END
#
# def get_registration_handler():
#     return ConversationHandler(
#         entry_points=[CommandHandler("register", register)],
#         states={
#             USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
#             PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
#             PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
#             ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
#         },
#         fallbacks=[CommandHandler("cancel", cancel)],
#     )

# Код продолжен...
# Обработчик команды /orders
AWAIT_ORDER_ID = 1

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



# Команда /manage_users для управления пользователями
AWAIT_USER_ID = 2

async def manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text(f"Список сотрудников и клиентов:\n```\n{table_str}\n```", parse_mode="Markdown")
        await update.message.reply_text("Введите ID пользователя для изменения его статуса:")
        return AWAIT_USER_ID

    except CustomUser.DoesNotExist:
        await update.message.reply_text("Ваш аккаунт не зарегистрирован как администратор.")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Ошибка в /manage_users: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка.")
        return ConversationHandler.END

async def update_user_is_staff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик для ввода ID пользователя и отображения кнопок смены статуса, включая "Отмена".
    """
    try:
        user_id = int(update.message.text)
        user = await sync_to_async(CustomUser.objects.get)(id=user_id, is_superuser=False)

        # Формируем сообщение и inline-кнопки
        status = "Сотрудник" if user.is_staff else "Клиент"
        user_info = (
            f"👤 **Пользователь #{user.id}**\n"
            f"Имя: {user.username}\n"
            f"Email: {user.email}\n"
            f"Текущий статус: {status}"
        )

        keyboard = [
            [InlineKeyboardButton("Сделать сотрудником", callback_data=f"staff_{user.id}_true")],
            [InlineKeyboardButton("Сделать клиентом", callback_data=f"staff_{user.id}_false")],
            [InlineKeyboardButton("Отмена", callback_data=f"cancel_user_status_{user.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(user_info, parse_mode="Markdown", reply_markup=reply_markup)
        return ConversationHandler.END

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


async def update_user_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Callback-обработчик для смены статуса is_staff или отмены.
    """
    query = update.callback_query
    await query.answer()

    try:
        callback_data = query.data
        if callback_data.startswith("cancel_user_status_"):
            # Обработка нажатия "Отмена"
            await query.delete_message()  # Удаляем сообщение с кнопками
            return

        # Извлекаем ID пользователя и новый статус
        _, user_id, is_staff = callback_data.split("_")
        user = await sync_to_async(CustomUser.objects.get)(id=user_id)

        # Обновляем статус is_staff
        user.is_staff = is_staff == "true"
        await sync_to_async(user.save)()

        new_status = "Сотрудник" if user.is_staff else "Клиент"
        await query.edit_message_text(f"✅ Статус пользователя #{user.id} изменён на '{new_status}'.")
    except Exception as e:
        logger.error(f"Ошибка при изменении статуса пользователя: {e}", exc_info=True)
        await query.edit_message_text("Произошла ошибка при изменении статуса.")


async def async_send_new_order_notification(order):
    try:
        # Получаем сотрудников с telegram_id
        staff_users = await sync_to_async(
            lambda: list(CustomUser.objects.filter(is_staff=True, telegram_id__isnull=False))
        )()

        # Проверка связи с элементами заказа
        logger.info(f"Fetching items for Order ID: {order.id}")
        order_items = await sync_to_async(lambda: list(order.items.prefetch_related("product").all()))()

        logger.info(f"Order Items Count: {len(order_items)}")
        for item in order_items:
            logger.info(f"Item: Product={item.product.name}, Quantity={item.quantity}, Price={item.price}")

        # Проверка order.user
        logger.info(f"Order User: {order.user.username}, Phone: {order.user.phone_number}")

        # Проверка самого заказа
        logger.info(f"Order Total Price: {order.total_price}, Address: {order.address}")

        # Получаем номер телефона клиента
        phone_number = order.user.phone_number if order.user.phone_number else "Не указан"

        # Формируем сообщение
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

        # Кнопка "Взять в работу"
        keyboard = [[InlineKeyboardButton("Взять в работу", callback_data=f"take_order_{order.id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Загружаем токен из переменной окружения
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ValueError("Токен Telegram бота отсутствует. Проверьте файл .env.")

        # Инициализация и отправка сообщений
        app = Application.builder().token(token).build()
        await app.initialize()  # Инициализация Application

        for staff in staff_users:
            logger.info(f"Sending message to {staff.username} ({staff.telegram_id})")
            await app.bot.send_message(
                chat_id=staff.telegram_id,
                text=order_message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )

        await app.shutdown()  # Завершаем работу Application
        logger.info("Notifications successfully sent.")

    except Exception as e:
        logger.error(f"Ошибка при отправке уведомлений: {e}", exc_info=True)


def send_new_order_notification(order):
    """
    Синхронная обёртка для вызова асинхронной функции отправки уведомлений.
    """
    asyncio.run(async_send_new_order_notification(order))

async def take_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик для кнопки "Взять в работу".
    """
    query = update.callback_query
    await query.answer()

    try:
        callback_data = query.data
        order_id = int(callback_data.split("_")[2])

        order = await sync_to_async(Order.objects.select_related("user").get)(id=order_id)

        if order.status != "created":
            await query.edit_message_text(f"⚠️ Заказ #{order.id} уже недоступен.")
            return

        order.status = "processing"
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=query.from_user.id)
        await sync_to_async(order.save)()

        await query.edit_message_text(f"✅ Вы взяли заказ #{order.id} в работу.")

        staff_users = await sync_to_async(
            lambda: list(CustomUser.objects.filter(is_staff=True, telegram_id__isnull=False).exclude(id=user.id))
        )()
        for staff in staff_users:
            await context.bot.send_message(
                chat_id=staff.telegram_id,
                text=f"⚠️ Заказ #{order.id} взят в работу сотрудником {user.username}."
            )

    except Order.DoesNotExist:
        await query.edit_message_text("❌ Этот заказ больше не существует.")
    except Exception as e:
        logger.error(f"Ошибка в take_order: {e}", exc_info=True)
        await query.edit_message_text("Произошла ошибка при обработке заказа.")

# Определяем состояния для ConversationHandler
CHOOSE_PERIOD, EXIT_ANALYTICS = range(2)


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


# Команда /analytics
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


# Обработчик выбора периода
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


# ConversationHandler для аналитики
def get_analytics_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("analytics", analytics)],
        states={
            CHOOSE_PERIOD: [CallbackQueryHandler(analytics_period_handler)],
        },
        fallbacks=[CallbackQueryHandler(analytics_period_handler)],
    )