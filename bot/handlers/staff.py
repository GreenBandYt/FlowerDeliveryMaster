



# Переносим функцию my_orders в другой модуль staff.py

async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    telegram_id = update.effective_user.id
    try:
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id, is_staff=True)
        orders = await sync_to_async(lambda: list(Order.objects.filter(status="processing", user_id=user.id)))()

        if not orders:
            await update.message.reply_text("\U0000274C У вас нет активных заказов в работе.")
            return ConversationHandler.END

        # Создание таблицы заказов
        table = PrettyTable(["#", "ID Заказа", "Сумма", "Адрес"])
        table.align["Адрес"] = "l"
        for idx, order in enumerate(orders, start=1):
            table.add_row([idx, order.id, f"{order.total_price:.2f} руб.", order.address or "Не указан"])

        await update.message.reply_text(
            f"Ваши текущие заказы в работе:\n<pre>{table}</pre>",
            parse_mode="HTML"
        )
        await update.message.reply_text(
            "Введите **ID заказа**, чтобы завершить его, или отправьте /cancel.",
            parse_mode="Markdown"
        )
        return AWAIT_ORDER_ID

    except CustomUser.DoesNotExist:
        await update.message.reply_text("\U0000274C У вас нет прав для выполнения этой команды.")
        return ConversationHandler.END

async def ask_complete_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        order_id = int(update.message.text.strip())  # Проверка корректности ввода
        telegram_id = update.effective_user.id

        # Проверка существования заказа
        user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id, is_staff=True)
        order = await sync_to_async(Order.objects.get)(id=order_id, status="processing", user_id=user.id)

        keyboard = [
            [InlineKeyboardButton("\u2705 Завершить заказ", callback_data=f"complete_order_{order_id}")],
            [InlineKeyboardButton("\u274C Отмена", callback_data=f"cancel_order_{order_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Вы выбрали заказ #{order.id}.\n"
            f"Сумма: {order.total_price:.2f} руб.\n"
            f"Адрес: {order.address or 'Не указан'}\n\n"
            "Подтвердите завершение заказа или отмените.",
            reply_markup=reply_markup
        )
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("\u274C Пожалуйста, введите корректный **ID заказа** (число).")
        return AWAIT_ORDER_ID

    except Order.DoesNotExist:
        await update.message.reply_text("\u274C Заказ с таким ID не найден. Попробуйте снова.")
        return AWAIT_ORDER_ID

async def complete_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    callback_data = query.data

    if callback_data.startswith("complete_order_"):
        order_id = callback_data.replace("complete_order_", "")
        try:
            order = await sync_to_async(Order.objects.get)(id=order_id, status="processing")
            order.status = "completed"
            await sync_to_async(order.save)()
            await query.edit_message_text(f"\u2705 Заказ #{order.id} успешно завершён.")
        except Order.DoesNotExist:
            await query.edit_message_text("\u274C Заказ не найден или уже завершён.")
        except Exception as e:
            logger.error(f"Ошибка при завершении заказа: {e}", exc_info=True)
            await query.edit_message_text("\u26A0 Произошла ошибка при завершении заказа.")

    elif callback_data.startswith("cancel_order_"):
        await query.edit_message_text("\u274C Действие отменено.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("\U0000274C Действие отменено.")
    return ConversationHandler.END

def get_my_orders_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("my_orders", my_orders)],
        states={
            AWAIT_ORDER_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_complete_order)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
