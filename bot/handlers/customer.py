from telegram import Update
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from catalog.models import Order  # Импортируем модель заказов

# Команда /view_orders
async def view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    try:
        # Проверяем заказы пользователя
        orders = await sync_to_async(Order.objects.filter)(user__telegram_id=user.id)
        if orders.exists():
            orders_text = "\n\n".join(
                [f"Заказ #{order.id} от {order.created_at.strftime('%d-%m-%Y')}:\nСтатус: {order.status}\nОбщая стоимость: {order.total_price}₽" for order in orders]
            )
            await update.message.reply_text(f"Ваши заказы:\n\n{orders_text}")
        else:
            await update.message.reply_text("У вас пока нет заказов.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при получении заказов: {e}")

# Команда /new_order
async def new_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Функционал создания нового заказа в разработке. Пожалуйста, используйте сайт для оформления."
    )
