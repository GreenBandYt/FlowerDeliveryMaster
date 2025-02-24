# time_settings.json

import asyncio
import logging
from telegram import Bot
from django.utils.timezone import now
from asgiref.sync import sync_to_async

from bot.utils.time_config import load_settings  # Добавляем импорт функции load_settings
from bot.utils.time_config import NEW_ORDER_NOTIFY_INTERVAL, REPEAT_ORDER_NOTIFY_INTERVAL
from bot.utils.time_utils import is_working_hours
from catalog.models import Order
from users.models import CustomUser

import os
from dotenv import load_dotenv  # Добавляем загрузку .env

# Загружаем переменные окружения
load_dotenv()

# Получаем токен из окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Настраиваем логирование
logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Глобальная переменная для последнего уведомления
LAST_NOTIFIED_AT = None


async def notification_worker():
    """
    Основной цикл обработки уведомлений о заказах.
    """
    global LAST_NOTIFIED_AT  # используем глобальную переменную

    if LAST_NOTIFIED_AT is None:
        LAST_NOTIFIED_AT = now()  # Инициализируем переменную при первом запуске

    while True:
        try:
            # Загрузим настройки перед каждой проверкой
            settings = load_settings()  # Получаем актуальные настройки

            # Теперь используем переменные из настроек
            NEW_ORDER_NOTIFY_INTERVAL = settings['new_order_notify_interval']
            REPEAT_ORDER_NOTIFY_INTERVAL = settings['repeat_order_notify_interval']

            if not is_working_hours():
                logger.info("⏳ Вне рабочего времени, уведомления не отправляются.")
            else:
                await process_new_orders()
                await process_repeat_notifications()

            logger.info(f"⏳ Следующая проверка через {NEW_ORDER_NOTIFY_INTERVAL} минут")
            await asyncio.sleep(NEW_ORDER_NOTIFY_INTERVAL * 60)

        except Exception as e:
            logger.error(f"❌ Ошибка в цикле уведомлений: {e}", exc_info=True)



async def process_new_orders():
    """
    Отправляет уведомления о новых заказах.
    """
    orders = await sync_to_async(lambda: list(Order.objects.filter(status="created")))()
    if not orders:
        logger.info("✅ Нет новых заказов для уведомлений.")
        return

    admins_and_staff = await get_admins_and_staff()

    for order in orders:
        if should_notify_order(order):
            message = await format_order_message(order)
            await send_notifications(admins_and_staff, message, order.id)

            logger.info(f"📨 Уведомление отправлено для заказа #{order.id}")




async def process_repeat_notifications():
    """
    Повторно отправляет уведомления, если заказ долго не берут.
    """
    global LAST_NOTIFIED_AT  # Используем глобальную переменную

    # Проверка интервала с последним уведомлением
    if LAST_NOTIFIED_AT is None or (now() - LAST_NOTIFIED_AT).total_seconds() > REPEAT_ORDER_NOTIFY_INTERVAL * 60:
        orders = await sync_to_async(lambda: list(Order.objects.filter(status="created")))()

        if not orders:
            logger.info("✅ Нет заказов для повторных уведомлений.")
            return

        admins_and_staff = await get_admins_and_staff()

        for order in orders:
            message = format_order_message(order, repeat=True)
            await send_notifications(admins_and_staff, message)

        # Обновляем время последнего уведомления
        LAST_NOTIFIED_AT = now()
        logger.info(f"🔄 Повторное уведомление отправлено для заказов")
    else:
        logger.info("⏳ Повторные уведомления еще не готовы для отправки.")


async def get_admins_and_staff():
    """
    Получает список администраторов и сотрудников с Telegram ID.
    """
    users = await sync_to_async(
        lambda: list(CustomUser.objects.filter(is_active=True, telegram_id__isnull=False))
    )()
    return [user.telegram_id for user in users if user.is_superuser or user.is_staff]


from telegram import InlineKeyboardMarkup, InlineKeyboardButton

async def send_notifications(user_ids, message, order_id):
    """
    Отправляет уведомление всем пользователям из списка.
    """
    for user_id in user_ids:
        try:
            user = await sync_to_async(lambda: CustomUser.objects.get(telegram_id=user_id))()

            # Если пользователь не администратор и не суперпользователь — добавляем кнопку
            if user.is_staff:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ Взять в работу", callback_data=f"staff_take_order:{order_id}")]
                ])
                await bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown", reply_markup=keyboard)
            else:
                # Администратору отправляем без кнопки
                await bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown")

            await asyncio.sleep(1)  # Чтобы не попасть под ограничение Telegram
        except Exception as e:
            logger.error(f"❌ Ошибка отправки уведомления пользователю {user_id}: {e}")


def should_notify_order(order):
    """
    Проверяет, нужно ли отправлять уведомление для заказа.
    """
    return True  # Отправляем уведомление для всех новых заказов


async def format_order_message(order, repeat=False):
    """
    Формирует текст уведомления о новом или повторном заказе.
    """
    # Получаем элементы заказа через sync_to_async
    order_items = await sync_to_async(
        lambda: "\n".join([f"📦 {item.product.name} - {item.quantity} шт." for item in order.items.all()])
    )()

    message_type = "🔄 Повторное уведомление!" if repeat else "🆕 Новый заказ!"

    # Получаем данные о пользователе через sync_to_async
    user = await sync_to_async(lambda: order.user)()

    return f"""
{message_type}

📝 *Оформление заказа:*
👤 *Покупатель:* {user.username}
📞 *Телефон:* {user.telegram_id}  
📍 *Адрес:* {order.address}

{order_items}
💰 *Итого:* {order.total_price} ₽
"""




if __name__ == "__main__":
    logging.info("🚀 Запуск системы уведомлений...")
    loop = asyncio.get_event_loop()
    loop.create_task(notification_worker())
    loop.run_forever()
