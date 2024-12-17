from telegram import Update
from telegram.ext import CallbackContext
from prettytable import PrettyTable
from catalog.models import Order
from users.models import CustomUser
import logging

# Настройка логгера
logger = logging.getLogger(__name__)

def view_orders(update: Update, context: CallbackContext):
    """
    Отображение истории заказов клиента.
    """
    user = update.effective_user

    try:
        logger.info(f"Пользователь {user.username} ({user.id}) отправил команду /view_orders")

        # Получаем заказы пользователя
        orders = Order.objects.filter(user__telegram_id=user.id).order_by('-created_at')
        logger.info(f"Найдено {len(orders)} заказов для пользователя {user.id}")

        if not orders:
            logger.info(f"У пользователя {user.username} ({user.id}) нет заказов.")
            update.message.reply_text("У вас пока нет заказов.")
            return

        # Создаем таблицу с помощью PrettyTable
        table = PrettyTable()
        table.field_names = ["ID заказа", "Дата", "Статус", "Сумма"]
        table.align["ID заказа"] = "l"
        table.align["Дата"] = "l"
        table.align["Статус"] = "l"
        table.align["Сумма"] = "r"

        for order in orders:
            table.add_row([
                order.id,
                order.created_at.strftime("%Y-%m-%d %H:%M"),
                order.get_status_display(),
                f"{order.total_price:.2f}",
            ])

        logger.info(f"Таблица заказов для пользователя {user.username} ({user.id}) успешно создана.")
        update.message.reply_text(f"Ваши заказы:\n```\n{table}\n```", parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка при обработке команды /view_orders для пользователя {user.username} ({user.id}): {e}", exc_info=True)
        update.message.reply_text("Произошла ошибка 33 при получении заказов.")
