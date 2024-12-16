from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import os
import re  # Импортируем модуль для работы с регулярными выражениями
from dotenv import load_dotenv
from users.models import CustomUser  # Импортируем модель CustomUser для взаимодействия с базой данных
from django.db.utils import IntegrityError
from asgiref.sync import sync_to_async  # Для работы с асинхронным контекстом
from prettytable import PrettyTable
from catalog.models import Order


import logging


# Настройка логгера
logger = logging.getLogger(__name__)


# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Состояния для регистрации
USERNAME, PASSWORD, PHONE, ADDRESS = range(4)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    # Проверяем, есть ли пользователь в базе данных
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id)

        if user.is_superuser:
            # Приветствие для администратора
            await update.message.reply_text(
                f"Здравствуйте, {user.username} (Администратор)!\n"
                "Доступные команды:\n"
                "/analytics - Просмотр аналитики\n"
                "/manage_users - Управление пользователями\n"
                "/orders - Управление заказами"
            )
        elif user.is_staff:
            # Приветствие для сотрудника
            await update.message.reply_text(
                f"Здравствуйте, {user.username} (Сотрудник)!\n"
                "Доступные команды:\n"
                "/orders - Управление заказами\n"
                "/update_status - Обновление статуса заказов"
            )
        else:
            # Приветствие для клиента
            await update.message.reply_text(
                f"Здравствуйте, {user.username} (Клиент)!\n"
                "Доступные команды:\n"
                "/view_orders - Просмотр ваших заказов\n"
                "/new_order - Создание нового заказа"
            )

    except CustomUser.DoesNotExist:
        # Если пользователь не найден, предлагаем привязать аккаунт
        await update.message.reply_text(
            "Здравствуйте! Ваш аккаунт не привязан.\n"
            "Введите /link <username>, чтобы привязать ваш Telegram аккаунт к системе."
        )

# Команда /link для привязки Telegram аккаунта к логину пользователя
async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Пожалуйста, укажите ваш логин. Пример: /link username")
        return

    username = context.args[0]
    telegram_id = update.effective_user.id

    try:
        user = await sync_to_async(CustomUser.objects.get)(username=username)

        if user.telegram_id and user.telegram_id != telegram_id:
            await update.message.reply_text(
                "Этот логин уже привязан к другому Telegram аккаунту."
            )
            return

        user.telegram_id = telegram_id
        await sync_to_async(user.save)()

        await update.message.reply_text(
            f"Ваш Telegram аккаунт успешно привязан к логину {username}."
        )

    except CustomUser.DoesNotExist:
        await update.message.reply_text("Пользователь с таким логином не найден.")

# Команда /register для регистрации нового пользователя
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите желаемое имя пользователя:",
        reply_markup=ReplyKeyboardMarkup([["Отмена"]], one_time_keyboard=True),
    )
    return USERNAME

# Получение имени пользователя
async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text

    if username.lower() == "отмена":
        await update.message.reply_text("Регистрация отменена.")
        return ConversationHandler.END

    context.user_data['username'] = username
    await update.message.reply_text("Введите пароль:")
    return PASSWORD

# Получение пароля
async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text
    context.user_data['password'] = password
    await update.message.reply_text("Введите ваш номер телефона:")
    return PHONE

# Получение телефона
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    context.user_data['phone'] = phone

    # Регулярное выражение для проверки формата номера телефона
    phone_pattern = r'^\+7\(\d{3}\)\d{3}-\d{2}-\d{2}$'

    # Валидация телефона
    if not re.match(phone_pattern, phone):
        await update.message.reply_text(
            "Ошибка: номер телефона должен быть в формате +7(XXX)XXX-XX-XX."
        )
        return PHONE

    await update.message.reply_text("Введите ваш адрес:")
    return ADDRESS

# Получение адреса и сохранение пользователя
async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text
    user_data = context.user_data

    try:
        user = await sync_to_async(CustomUser.objects.create_user)(
            username=user_data['username'],
            password=user_data['password'],
            telegram_id=update.effective_user.id,
            phone_number=user_data['phone'],
            address=address,
        )
        await sync_to_async(user.save)()
        await update.message.reply_text("Регистрация успешна! Теперь вы можете использовать бота.")
    except IntegrityError:
        await update.message.reply_text(
            "Ошибка: такое имя пользователя уже существует. Попробуйте снова."
        )
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

    return ConversationHandler.END

# Обработка отмены
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Регистрация отменена.")
    return ConversationHandler.END

# Функция для возврата ConversationHandler для регистрации
def get_registration_handler():
    """
    Возвращает ConversationHandler для регистрации пользователя.
    """
    return ConversationHandler(
        entry_points=[CommandHandler("register", register)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

# Команда /orders для управления заказами
async def orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    try:
        # Проверяем пользователя
        logger.info(f"Обработчик команды /orders запущен для пользователя {update.effective_user.username} ({telegram_id})")
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id)
        logger.info(f"Пользователь найден: {user.username} (ID: {user.id})")

        # Проверяем права доступа
        if not (user.is_superuser or user.is_staff):
            logger.warning(f"Доступ к /orders запрещен для {user.username} ({telegram_id}).")
            await update.message.reply_text("У вас нет доступа к этой команде.")
            return

        # Загружаем заказы
        logger.info("Загрузка заказов из базы данных...")
        all_orders = await sync_to_async(lambda: list(Order.objects.select_related('user').all()))()

        logger.info(f"Найдено заказов: {len(all_orders)}")

        if not all_orders:
            logger.info("Нет заказов в базе данных.")
            await update.message.reply_text("Заказов пока нет.")
            return

        # Формируем таблицу
        logger.info(f"Формирование таблицы заказов...")
        table = PrettyTable(["ID", "Дата", "Статус", "Сумма", "Клиент"])
        for order in all_orders:
            table.add_row([
                order.id,
                order.created_at.strftime("%Y-%m-%d %H:%M"),
                order.get_status_display() if hasattr(order, 'get_status_display') else order.status,
                f"{order.total_price:.2f} руб." if order.total_price else "0.00 руб.",
                order.user.username if order.user else "Не указан"
            ])

        # Отправка таблицы
        table_str = table.get_string()
        max_message_length = 4000
        if len(table_str) > max_message_length:
            chunks = [table_str[i:i + max_message_length] for i in range(0, len(table_str), max_message_length)]
            for chunk in chunks:
                await update.message.reply_text(f"```\n{chunk}\n```", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"Все заказы:\n```\n{table_str}\n```", parse_mode="Markdown")

        logger.info(f"Таблица заказов успешно отправлена для пользователя {user.username} ({telegram_id}).")

    except CustomUser.DoesNotExist:
        logger.warning(f"Пользователь с telegram_id={telegram_id} не найден.")
        await update.message.reply_text("Ваш аккаунт не зарегистрирован в системе.")
    except Exception as e:
        logger.error(f"Ошибка в обработке команды /orders: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка при получении заказов.")
