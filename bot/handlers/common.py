from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from users.models import CustomUser
from asgiref.sync import sync_to_async
from django.db.utils import IntegrityError
import re

# Состояния для регистрации
USERNAME, PASSWORD, PHONE, ADDRESS = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start. Приветствует пользователя в зависимости от его роли.
    """
    telegram_id = update.effective_user.id

    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id)

        if user.is_superuser:
            await update.message.reply_text(
                f"Здравствуйте, {user.username} (Администратор)!\n"
                "Доступные команды:\n"
                "/analytics - Просмотр аналитики\n"
                "/manage_users - Управление пользователями\n"
                "/orders - Управление заказами"
            )
        elif user.is_staff:
            await update.message.reply_text(
                f"Здравствуйте, {user.username} (Сотрудник)!\n"
                "Доступные команды:\n"
                "/orders - Управление заказами\n"
                "/update_status - Обновление статуса заказов"
            )
        else:
            await update.message.reply_text(
                f"Здравствуйте, {user.username} (Клиент)!\n"
                "Доступные команды:\n"
                "/view_orders - Просмотр ваших заказов\n"
                "/new_order - Создание нового заказа"
            )

    except CustomUser.DoesNotExist:
        await update.message.reply_text(
            "Здравствуйте! Ваш аккаунт не привязан.\n"
            "Введите /link <username>, чтобы привязать ваш Telegram аккаунт к системе."
        )

async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Привязывает Telegram аккаунт пользователя к логину в системе.
    """
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

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Начало процесса регистрации.
    """
    await update.message.reply_text(
        "Введите желаемое имя пользователя:",
        reply_markup=ReplyKeyboardMarkup([["Отмена"]], one_time_keyboard=True),
    )
    return USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получение имени пользователя для регистрации.
    """
    username = update.message.text

    if username.lower() == "отмена":
        await update.message.reply_text("Регистрация отменена.")
        return ConversationHandler.END

    context.user_data['username'] = username
    await update.message.reply_text("Введите пароль:")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получение пароля для регистрации.
    """
    password = update.message.text
    context.user_data['password'] = password
    await update.message.reply_text("Введите ваш номер телефона:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получение телефона для регистрации.
    """
    phone = update.message.text
    context.user_data['phone'] = phone

    # Регулярное выражение для проверки формата номера телефона
    phone_pattern = r'^\+7\(\d{3}\)\d{3}-\d{2}-\d{2}$'

    if not re.match(phone_pattern, phone):
        await update.message.reply_text(
            "Ошибка: номер телефона должен быть в формате +7(XXX)XXX-XX-XX."
        )
        return PHONE

    await update.message.reply_text("Введите ваш адрес:")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получение адреса и завершение регистрации.
    """
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

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отмена регистрации.
    """
    await update.message.reply_text("Регистрация отменена.")
    return ConversationHandler.END

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
