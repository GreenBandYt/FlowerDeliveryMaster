from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    CommandHandler,
    filters,
)
from asgiref.sync import sync_to_async
from catalog.models import Order  # Импортируем модель заказов
from users.models import CustomUser  # Импортируем модель пользователей
from bot.handlers.customer import view_orders  # Импортируем функцию для команды /view_orders

# Состояния для ConversationHandler
ORDER_ID, NEW_STATUS = range(2)

async def start_update_status(update, context: ContextTypes.DEFAULT_TYPE):
    """
    Начинает процесс обновления статуса заказа.
    """
    telegram_id = update.effective_user.id

    try:
        # Проверяем, является ли пользователь сотрудником
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id)

        if not user.is_staff:
            await update.message.reply_text("У вас нет доступа к этой команде.")
            return ConversationHandler.END

        await update.message.reply_text("Введите ID заказа, который вы хотите обновить:")
        return ORDER_ID

    except CustomUser.DoesNotExist:
        await update.message.reply_text("Ваш аккаунт не найден в системе.")
        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")
        return ConversationHandler.END

async def get_order_id(update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получает ID заказа и запрашивает новый статус.
    """
    order_id = update.message.text
    context.user_data['order_id'] = order_id

    try:
        # Проверяем, существует ли заказ
        order = await sync_to_async(Order.objects.get)(id=order_id)

        # Предлагаем выбрать новый статус
        statuses = ['created', 'processed', 'shipped', 'delivered']
        keyboard = [[status] for status in statuses]
        await update.message.reply_text(
            "Выберите новый статус заказа:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True),
        )
        return NEW_STATUS

    except Order.DoesNotExist:
        await update.message.reply_text("Заказ с указанным ID не найден. Попробуйте снова.")
        return ORDER_ID
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")
        return ConversationHandler.END

async def update_order_status(update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обновляет статус заказа.
    """
    new_status = update.message.text
    order_id = context.user_data.get('order_id')

    try:
        order = await sync_to_async(Order.objects.get)(id=order_id)
        order.status = new_status
        await sync_to_async(order.save)()

        await update.message.reply_text(
            f"Статус заказа #{order_id} успешно обновлен на '{new_status}'."
        )
        return ConversationHandler.END

    except Order.DoesNotExist:
        await update.message.reply_text("Заказ с указанным ID не найден. Попробуйте снова.")
        return ORDER_ID
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")
        return ConversationHandler.END

async def cancel(update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает отмену операции.
    """
    await update.message.reply_text("Обновление статуса заказа отменено.")
    return ConversationHandler.END

def get_update_status_handler():
    """
    Возвращает ConversationHandler для обновления статуса заказа.
    """
    return ConversationHandler(
        entry_points=[MessageHandler(filters.COMMAND & filters.Regex("^/update_status$"), start_update_status)],
        states={
            ORDER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_order_id)],
            NEW_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, update_order_status)],
        },
        fallbacks=[MessageHandler(filters.COMMAND & filters.Regex("^/cancel$"), cancel)],
    )

# Регистрация команды /view_orders
def register_handlers(application):
    """
    Регистрирует все обработчики команд в приложении.
    """
    application.add_handler(CommandHandler("view_orders", view_orders))  # Команда для просмотра заказов
    application.add_handler(get_update_status_handler())  # Команда для обновления статуса
