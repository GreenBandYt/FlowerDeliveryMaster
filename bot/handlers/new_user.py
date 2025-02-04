# bot/handlers/new_user.py

import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from users.models import CustomUser
from asgiref.sync import sync_to_async
from django.db.utils import IntegrityError
import re
from bot.keyboards.new_user_keyboards import new_user_keyboard

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Состояния для регистрации
USERNAME, PASSWORD, PHONE, ADDRESS = range(4)

async def new_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Приветствие незарегистрированного пользователя.
    """
    keyboard = new_user_keyboard
    await update.message.reply_text(
        "👋 Добро пожаловать в систему!\n"
        "Ваш аккаунт не привязан.\n\n"
        "🔗 Используйте команду /link для привязки существующего аккаунта.\n"
        "📝 Или выберите /register чтобы создать новый аккаунт.\n"
        "ℹ️ Воспользуйтесь командой /help_new_user для получения помощи.",
        reply_markup=keyboard
    )

async def help_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Помощь для незарегистрированного пользователя.
    """
    await update.message.reply_text(
        "ℹ️ **Помощь для незарегистрированного пользователя:**\n\n"
        "🔗 /link - Привязать аккаунт.\n"
        "📝 /register - Зарегистрироваться в системе.\n"
        "👀 /help_new_user - Показать это сообщение."
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
        fallbacks=[],
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

    existing_user = await sync_to_async(CustomUser.objects.filter(username=username).exists)()
    if existing_user:
        await update.message.reply_text("❌ Такое имя пользователя уже существует. Попробуйте другое имя.")
        return USERNAME

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
