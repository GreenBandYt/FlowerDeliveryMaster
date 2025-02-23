# bot/handlers/new_user.py

import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
from users.models import CustomUser
from asgiref.sync import sync_to_async
from django.db.utils import IntegrityError
import re
from bot.keyboards.new_user_keyboards import new_user_keyboard
from bot.handlers.customer import customer_start


# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Состояния для регистрации
# USERNAME, PASSWORD, PHONE, ADDRESS = range(4)

async def new_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Приветствие незарегистрированного пользователя.
    Устанавливает состояние 'new_user_start' и роль 'new_user', затем отправляет сообщение с клавиатурой.
    """
    # Устанавливаем роль и состояние для нового пользователя
    context.user_data["role"] = "new_user"
    context.user_data["state"] = "new_user_start"
    logger.info(f"[NEW_USER_START] Установлено состояние 'new_user_start' для пользователя {update.effective_user.id}")

    # Отправка приветственного сообщения с клавиатурой
    keyboard = new_user_keyboard
    await update.message.reply_text(
        "👋 Здравствуйте!\n"
        "Ваш аккаунт не привязан.\n"
        "Воспользуйтесь кнопками меню:\n"
        "🔗 Привязать аккаунт\n"
        "📝 Зарегистрироваться\n"
        "🆘 Помощь",
        reply_markup=keyboard,
    )
    logger.info(f"[NEW_USER_START] Приветственное сообщение отправлено пользователю {update.effective_user.id}")


async def handle_new_user_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Помощь для незарегистрированного пользователя.
    """
    keyboard = new_user_keyboard
    await update.message.reply_text(
        "ℹ️ **Помощь для незарегистрированного пользователя:**\n\n"
        "Воспользуйтесь кнопками меню:\n"
        "🔗 Привязать аккаунт\n"
        "📝 Зарегистрироваться\n"
        "🆘 Помощь",
        reply_markup=keyboard,
    )


async def handle_new_user_link_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    1) Устанавливает состояние AWAIT_LINK.
    2) Просит пользователя ввести логин.
    """
    telegram_id = update.effective_user.id
    logger.info(f"[LINK_START] Пользователь {telegram_id} нажал кнопку «Привязать аккаунт».")

    # Устанавливаем состояние "AWAIT_LINK"
    context.user_data["state"] = "AWAIT_LINK"

    # Отправляем сообщение с просьбой ввести логин
    await update.message.reply_text("Пожалуйста, введите ваш логин:")
    logger.info(f"[LINK_START] Установлено состояние AWAIT_LINK для пользователя {telegram_id}.")


async def handle_new_user_link_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    1) Проверяет введённый логин.
    2) Привязывает Telegram к логину в БД.
    3) Возвращает состояние в "new_user_start" (или любое другое).
    """
    telegram_id = update.effective_user.id
    username = update.message.text.strip()

    logger.info(f"[LINK_INPUT] Пользователь {telegram_id} ввёл логин: {username}")

    # Валидация логина
    if not re.match(r"^\w{3,}$", username):
        await update.message.reply_text(
            "❌ Логин должен состоять минимум из 3 символов (буквы, цифры, подчёркивания). Попробуйте снова."
        )
        return

    # Пытаемся найти пользователя с указанным логином
    try:
        user = await sync_to_async(CustomUser.objects.get)(username=username)

        # Проверяем, не привязан ли уже этот логин к другому Telegram ID
        if user.telegram_id and user.telegram_id != telegram_id:
            await update.message.reply_text("⚠️ Этот логин уже привязан к другому Telegram-аккаунту.")
            return

        # Привязываем
        user.telegram_id = telegram_id
        await sync_to_async(user.save)()

        await update.message.reply_text(f"✅ Telegram успешно привязан к логину {username}.")

        # Возвращаем состояние обратно, например, в new_user_start
        context.user_data["state"] = "new_user_start"
        logger.info(f"[LINK_SUCCESS] Пользователь {telegram_id} вернулся в состояние new_user_start.")

    except CustomUser.DoesNotExist:
        await update.message.reply_text("❌ Пользователь с таким логином не найден. Попробуйте снова.")


async def handle_new_user_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Начало процесса регистрации нового пользователя.
    Устанавливает состояние регистрации на USERNAME и отправляет сообщение с просьбой ввести желаемое имя.
    """
    # Устанавливаем роль нового пользователя и состояние регистрации
    context.user_data["role"] = "new_user"
    context.user_data["state"] = "USERNAME"
    logger.info(
        f"[REGISTER] Пользователь {update.effective_user.id} начинает регистрацию. Состояние установлено: USERNAME")

    # Отправляем сообщение с просьбой ввести имя пользователя
    await update.message.reply_text("📝 Введите желаемое имя пользователя:")

async def handle_new_user_get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получение имени пользователя для регистрации.
    Обрабатывает введённое имя, проверяет его уникальность и переводит пользователя к вводу пароля.
    """
    username = update.message.text.strip()

    # Обработка отмены регистрации
    if username.lower() == "отмена":
        await update.message.reply_text("🚫 Регистрация отменена.")
        # Переводим пользователя в состояние главного меню (например, new_user_start)
        context.user_data["state"] = "new_user_start"
        return

    # Проверяем, существует ли уже пользователь с таким именем
    existing_user = await sync_to_async(CustomUser.objects.filter(username=username).exists)()
    if existing_user:
        await update.message.reply_text("❌ Такое имя пользователя уже существует. Попробуйте другое имя.")
        # Оставляем состояние как "USERNAME" для повторного ввода
        context.user_data["state"] = "USERNAME"
        return

    # Сохраняем введённое имя и переводим в следующий шаг регистрации
    context.user_data['username'] = username
    context.user_data["state"] = "PASSWORD"
    await update.message.reply_text("🔒 Введите пароль:")


async def handle_new_user_get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получение пароля для регистрации.
    Сохраняет введённый пароль в context.user_data и переводит пользователя к следующему шагу (ввод номера телефона).
    """
    password = update.message.text.strip()

    # Обработка отмены
    if password.lower() == "отмена":
        await update.message.reply_text("🚫 Регистрация отменена.")
        context.user_data["state"] = "new_user_start"
        return

    # Сохраняем пароль (он будет хэшироваться в финальном шаге при создании пользователя)
    context.user_data['password'] = password

    # Переводим пользователя к следующему шагу (ввод телефона)
    context.user_data["state"] = "PHONE"
    await update.message.reply_text("📞 Введите ваш номер телефона в формате +7(XXX)XXX-XX-XX:")

    logger.info(f"[REGISTER] Пользователь {update.effective_user.id} ввёл пароль и переходит к вводу телефона.")

import re
import logging

logger = logging.getLogger(__name__)

async def handle_new_user_get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получение телефона для регистрации.
    """
    phone = update.message.text.strip()

    # Обработка отмены
    if phone.lower() == "отмена":
        await update.message.reply_text("🚫 Регистрация отменена.")
        context.user_data["state"] = "new_user_start"
        return

    # Проверка формата телефона
    phone_pattern = r'^\+7\(\d{3}\)\d{3}-\d{2}-\d{2}$'
    if not re.match(phone_pattern, phone):
        await update.message.reply_text(
            "❌ Номер телефона должен быть в формате +7(XXX)XXX-XX-XX. Попробуйте снова."
        )
        context.user_data["state"] = "PHONE"  # Оставляем пользователя в текущем шаге
        return

    # Сохраняем телефон в context.user_data
    context.user_data['phone'] = phone

    # Переход к следующему шагу
    context.user_data["state"] = "ADDRESS"
    await update.message.reply_text("🏠 Введите ваш адрес:")

    logger.info(f"[REGISTER] Пользователь {update.effective_user.id} ввёл номер телефона и переходит к вводу адреса.")



async def handle_new_user_get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получение адреса и завершение регистрации.
    """
    address = update.message.text.strip()

    # Обработка отмены
    if address.lower() == "отмена":
        await update.message.reply_text("🚫 Регистрация отменена.")
        context.user_data["state"] = "new_user_start"
        return

    user_data = context.user_data

    try:
        # Создаём пользователя через create_user (он автоматически хэширует пароль)
        user = await sync_to_async(CustomUser.objects.create_user)(
            username=user_data['username'],
            password=user_data['password'],  # set_password вызовется автоматически
            telegram_id=update.effective_user.id,
            phone_number=user_data['phone'],
            address=address,
        )

        await update.message.reply_text("✅ Регистрация успешно завершена! 🎉")

        logger.info(f"[REGISTER] Пользователь {update.effective_user.id} успешно зарегистрирован.")

        # После регистрации направляем пользователя в customer_start (потому что он становится клиентом)
        await customer_start(update, context)

        logger.info(f"[REGISTER] Пользователь {update.effective_user.id} успешно зарегистрирован.")


    except IntegrityError:
        await update.message.reply_text("❌ Такой пользователь уже существует. Попробуйте другое имя.")
        context.user_data["state"] = "USERNAME"  # Возвращаем пользователя на шаг ввода имени

    except Exception as e:
        logger.error(f"[REGISTER ERROR] Ошибка регистрации пользователя {update.effective_user.id}: {e}", exc_info=True)
        await update.message.reply_text(f"⚠️ Произошла ошибка при регистрации. Попробуйте позже.")
        context.user_data["state"] = "new_user_start"  # Сбрасываем в начальное состояние