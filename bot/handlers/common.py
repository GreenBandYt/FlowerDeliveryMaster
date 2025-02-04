from telegram import Update
from telegram.ext import ContextTypes
from users.models import CustomUser
from asgiref.sync import sync_to_async
import logging

from bot.handlers.admin import admin_start
from bot.handlers.staff import staff_start
from bot.handlers.customer import customer_start
from bot.handlers.new_user import new_user_start

from bot.dictionaries.text_actions import TEXT_ACTIONS
from bot.dictionaries.callback_actions import CALLBACK_ACTIONS
from django.core.cache import cache

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ======== Обработчик команды /start ========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start. Приветствует пользователя в зависимости от его роли
    и добавляет меню с кнопками.
    """
    telegram_id = update.effective_user.id
    try:
        # Получаем пользователя по Telegram ID
        user = await sync_to_async(CustomUser.objects.filter(telegram_id=telegram_id).first)()

        if user:
            # Логирование успешной идентификации роли
            logger.info(f"Пользователь найден: {user.username}, superuser={user.is_superuser}, staff={user.is_staff}")

            # Определяем роль и вызываем соответствующую функцию
            if user.is_superuser:
                await admin_start(update, context)
            elif user.is_staff:
                await staff_start(update, context)
            else:
                await customer_start(update, context)
        else:
            # Логирование отсутствия пользователя
            logger.warning(f"Пользователь с Telegram ID {telegram_id} не найден.")
            # Перенаправляем незарегистрированного пользователя
            await new_user_start(update, context)
    except Exception as e:
        # Логирование ошибок
        logger.error(f"Ошибка при обработке команды /start: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте позже.")

# ======== Универсальный обработчик текста ========
async def handle_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Универсальный обработчик текста от пользователя.
    """
    user_text = update.message.text.strip()
    telegram_id = update.effective_user.id

    # Определяем роль пользователя
    role = cache.get(f"user_role_{telegram_id}")
    if not role:
        user = await sync_to_async(CustomUser.objects.filter(telegram_id=telegram_id).first)()
        if user:
            role = "admin" if user.is_superuser else "manager" if user.is_staff else "customer"
            cache.set(f"user_role_{telegram_id}", role, timeout=3600)
        else:
            role = "new_user"

    # Проверяем текстовые команды в словаре
    action = TEXT_ACTIONS.get(user_text)

    if action:
        await action(update, context)  # Вызываем функцию напрямую
        return

    # Если ничего не найдено, отправляем сообщение по умолчанию
    await update.message.reply_text(
        "Извините, я вас не понял. Попробуйте уточнить запрос или воспользуйтесь кнопками меню. 🤔"
    )

# ======== Универсальный обработчик inline-кнопок ========
async def handle_inline_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Универсальный обработчик для инлайн-кнопок.
    """
    query = update.callback_query
    await query.answer()  # Подтверждаем нажатие кнопки

    callback_data = query.data  # Получаем callback_data кнопки
    logging.info(f"Получено callback_data: {callback_data}")

    # Проверяем наличие callback_data в словаре
    action = CALLBACK_ACTIONS.get(callback_data)
    if action:
        try:
            # Вызываем функцию напрямую из словаря
            await globals()[action](update, context)
        except KeyError:
            logging.error(f"Функция для callback_data '{callback_data}' не найдена.")
            await query.edit_message_text(
                "Произошла ошибка при выполнении действия. Обратитесь к администратору."
            )
    else:
        # Если callback_data отсутствует в словаре
        logging.warning(f"Неизвестное callback_data: {callback_data}")
        await query.edit_message_text(
            "Кнопка больше не активна. Попробуйте снова или обратитесь к администратору."
        )
