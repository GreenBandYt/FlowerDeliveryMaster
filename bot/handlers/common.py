# bot/handlers/common.py

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (ContextTypes, CommandHandler, ConversationHandler,
                          MessageHandler, filters)
from users.models import CustomUser

from asgiref.sync import sync_to_async
from django.db.utils import IntegrityError
import re
import logging

from bot.handlers.admin import admin_start
from bot.handlers.staff import staff_start
from bot.handlers.customer import customer_start

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Состояния для регистрации
USERNAME, PASSWORD, PHONE, ADDRESS = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start. Приветствует пользователя в зависимости от его роли
    и добавляет меню с кнопками.
    """
    telegram_id = update.effective_user.id
    try:
        # Получаем пользователя по Telegram ID
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id)
        # Определяем роль и вызываем соответствующую функцию
        if user.is_superuser:
            await admin_start(update, context)
        elif user.is_staff:
            await staff_start(update, context)
        else:
            await customer_start(update, context)
    except CustomUser.DoesNotExist:
        # Обработка для незарегистрированных пользователей
        keyboard = ReplyKeyboardMarkup(
            [["🔗 Привязать аккаунт", "📝 Зарегистрироваться"], ["ℹ️ Помощь"]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await update.message.reply_text(
            "👋 Добро пожаловать в систему!\n"
            "Ваш аккаунт не привязан.\n\n"
            "🔗 Используйте команду /link для привязки существующего аккаунта.\n"
            "📝 Или выберите /register чтобы создать новый аккаунт.\n"
            "ℹ️ Воспользуйтесь командой /show_help для получения помощи.",
            reply_markup=keyboard
        )

async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Привязывает Telegram аккаунт пользователя к логину в системе.
    """
    if len(context.args) != 1:
        await update.message.reply_text("⚠️ Укажите логин. Пример: /link your_username")
        return

    username = context.args[0]
    telegram_id = update.effective_user.id

    if not re.match(r"^\w{3,}$", username):
        await update.message.reply_text("❌ Логин должен состоять минимум из 3 символов. Попробуйте снова.")
        return

    try:
        user = await sync_to_async(CustomUser.objects.get)(username=username)

        if user.telegram_id and user.telegram_id != telegram_id:
            await update.message.reply_text(
                "⚠️ Этот логин уже привязан к другому Telegram аккаунту."
            )
            return

        user.telegram_id = telegram_id
        await sync_to_async(user.save)()

        await update.message.reply_text(
            f"✅ Telegram успешно привязан к логину {username}."
        )
    except CustomUser.DoesNotExist:
        await update.message.reply_text("❌ Пользователь с таким логином не найден.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отмена текущего действия.
    """
    await update.message.reply_text("🚫 Действие отменено.")
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

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Начало процесса регистрации.
    """
    await update.message.reply_text(
        "📝 Введите желаемое имя пользователя:"
    )
    return USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получение имени пользователя для регистрации.
    """
    username = update.message.text

    if username.lower() == "отмена":
        await update.message.reply_text("🚫 Регистрация отменена.")
        return ConversationHandler.END

    context.user_data['username'] = username
    await update.message.reply_text("🔒 Введите пароль:")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получение пароля для регистрации.
    """
    password = update.message.text
    context.user_data['password'] = password
    await update.message.reply_text("📞 Введите ваш номер телефона:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получение телефона для регистрации.
    """
    phone = update.message.text
    context.user_data['phone'] = phone

    phone_pattern = r'^\+7\(\d{3}\)\d{3}-\d{2}-\d{2}$'
    if not re.match(phone_pattern, phone):
        await update.message.reply_text(
            "❌ Номер телефона должен быть в формате +7(XXX)XXX-XX-XX."
        )
        return PHONE

    await update.message.reply_text("🏠 Введите ваш адрес:")
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
        await update.message.reply_text("✅ Регистрация успешна!")
    except IntegrityError:
        await update.message.reply_text("❌ Такое имя пользователя уже существует.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Произошла ошибка: {e}")

    return ConversationHandler.END
