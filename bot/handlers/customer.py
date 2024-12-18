from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from asgiref.sync import sync_to_async
from prettytable import PrettyTable
from catalog.models import Product, Cart, CartItem, Order, OrderItem
import logging

# Настройка логгера
logger = logging.getLogger(__name__)


# ======= Просмотр каталога товаров =======
async def view_catalog(update: Update, context: CallbackContext):
    """
    Отображение списка товаров с инлайн-кнопками для добавления в корзину.
    """
    user = update.effective_user

    try:
        logger.info(f"Пользователь {user.username} ({user.id}) вызвал команду /view_catalog")

        # Получаем список товаров из базы данных
        products = await sync_to_async(lambda: list(Product.objects.all()))()
        if not products:
            await update.message.reply_text("Каталог пуст.")
            return

        # Формируем сообщение с товарами и инлайн-кнопками
        for product in products:
            text = (f"Предложение: {product.id}\n"
                    f"\U0001F4E6 {product.name}\n"
                    f"\U0001F4B0 Цена: {product.price:.2f} руб.\n"
                    f"\u2139\ufe0f {product.description}")

            # Инлайн-кнопка для добавления в корзину
            keyboard = [[InlineKeyboardButton(
                "Добавить в корзину",
                callback_data=f"add_to_cart_{product.id}"
            )]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(text, reply_markup=reply_markup)

    except Exception as e:
        logger.exception(f"Ошибка при отображении каталога для пользователя {user.username} ({user.id}): {e}")
        await update.message.reply_text("Произошла ошибка при загрузке каталога.")

# ======= Обработка добавления товара в корзину =======
async def add_to_cart(update: Update, context: CallbackContext):
    """
    Добавление товара в корзину пользователя по callback-запросу.
    """
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()
        product_id = int(query.data.split('_')[-1])

        # Получаем товар из базы данных
        product = await sync_to_async(Product.objects.get)(id=product_id)

        # Получаем или создаем корзину пользователя
        cart, _ = await sync_to_async(Cart.objects.get_or_create)(user__telegram_id=user.id)

        # Проверяем, есть ли товар уже в корзине
        cart_item, created = await sync_to_async(CartItem.objects.get_or_create)(
            cart=cart, product=product,
            defaults={"quantity": 1, "price": product.price}
        )
        if not created:
            cart_item.quantity += 1
            cart_item.price = cart_item.quantity * product.price
            await sync_to_async(cart_item.save)()

        logger.info(f"Товар {product.name} добавлен в корзину пользователя {user.username} ({user.id}).")
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(f"\U0001F4E6 Товар '{product.name}' добавлен в вашу корзину!")

    except Product.DoesNotExist:
        logger.error(f"Товар с ID {product_id} не найден.")
        await query.message.reply_text("Ошибка: товар не найден.")
    except Exception as e:
        logger.exception(f"Ошибка при добавлении товара в корзину: {e}")
        await query.message.reply_text("Произошла ошибка при добавлении товара в корзину.")


async def remove_from_cart(update: Update, context: CallbackContext):
    """
    Удаление товара из корзины пользователя по callback-запросу.
    """
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()
        product_id = int(query.data.split('_')[-1])

        # Получаем корзину пользователя
        cart = await sync_to_async(Cart.objects.get)(user__telegram_id=user.id)

        # Получаем товар в корзине
        cart_item = await sync_to_async(CartItem.objects.get)(cart=cart, product_id=product_id)

        # Уменьшаем количество товара или удаляем из корзины
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.price = cart_item.quantity * cart_item.product.price
            await sync_to_async(cart_item.save)()
        else:
            await sync_to_async(cart_item.delete)()

        logger.info(f"Товар с ID {product_id} удалён из корзины пользователя {user.username} ({user.id}).")
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("\U0001F6AE Товар удалён из вашей корзины.")

    except Cart.DoesNotExist:
        logger.error(f"Корзина пользователя {user.username} ({user.id}) не найдена.")
        await query.message.reply_text("Ошибка: корзина не найдена.")
    except CartItem.DoesNotExist:
        logger.error(f"Товар с ID {product_id} отсутствует в корзине пользователя {user.username} ({user.id}).")
        await query.message.reply_text("Ошибка: товар не найден в вашей корзине.")
    except Exception as e:
        logger.exception(f"Ошибка при удалении товара из корзины: {e}")
        await query.message.reply_text("Произошла ошибка при удалении товара из корзины.")


async def confirm_checkout(update: Update, context: CallbackContext):
    """
    Подтверждение оформления заказа из корзины.
    """
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        # Получаем корзину пользователя
        cart = await sync_to_async(Cart.objects.get)(user__telegram_id=user.id)

        # Проверяем, есть ли товары в корзине
        if not cart.items.exists():
            await query.message.reply_text("\U0001F6D2 Ваша корзина пуста.")
            return

        # Создаем заказ на основе корзины
        order = await sync_to_async(Order.objects.create)(
            user=cart.user,
            total_price=sum(item.price for item in cart.items.all())
        )
        for item in cart.items.all():
            await sync_to_async(order.items.create)(
                product=item.product,
                quantity=item.quantity,
                price=item.price
            )
        await sync_to_async(cart.items.all().delete)()  # Очищаем корзину

        logger.info(f"Пользователь {user.username} ({user.id}) оформил заказ {order.id}.")
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("\U0001F4E6 Ваш заказ успешно оформлен!")

    except Cart.DoesNotExist:
        logger.error(f"Корзина пользователя {user.username} ({user.id}) не найдена.")
        await query.message.reply_text("Ошибка: корзина не найдена.")
    except Exception as e:
        logger.exception(f"Ошибка при подтверждении оформления заказа: {e}")
        await query.message.reply_text("Произошла ошибка при оформлении заказа.")

async def cancel_checkout(update: Update, context: CallbackContext):
    """
    Отмена оформления заказа.
    """
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        logger.info(f"Пользователь {user.username} ({user.id}) отменил оформление заказа.")
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("\U0001F6AB Оформление заказа отменено. Вы можете продолжить покупки.")

    except Exception as e:
        logger.exception(f"Ошибка при отмене оформления заказа: {e}")
        await query.message.reply_text("Произошла ошибка при отмене оформления заказа.")


# ======= Просмотр корзины =======
async def view_cart(update: Update, context: CallbackContext):
    """
    Отображение содержимого корзины пользователя с итоговой суммой и кнопкой перехода к оформлению заказа.
    """
    user = update.effective_user

    try:
        logger.info(f"Пользователь {user.username} ({user.id}) вызвал команду /view_cart")

        # Получаем корзину пользователя
        cart_items = await sync_to_async(
            lambda: list(CartItem.objects.filter(cart__user__telegram_id=user.id).select_related('product'))
        )()

        if not cart_items:
            await update.message.reply_text("Ваша корзина пуста.")
            return

        # Формируем сообщение с содержимым корзины
        total_price = 0
        message = "🛒 <b>Ваша корзина:</b>\n\n"
        for item in cart_items:
            product_name = item.product.name
            total_price += item.price
            message += (
                f"📦 {product_name}\n"
                f"Количество: {item.quantity}\n"
                f"Цена: {item.price} ₽\n\n"
            )

        message += f"💰 <b>Итого: {total_price} ₽</b>"

        # Добавляем кнопку перехода к оформлению заказа
        keyboard = [[InlineKeyboardButton("📝 Оформить заказ", callback_data="checkout")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="HTML")

    except Exception as e:
        logger.exception(f"Ошибка при просмотре корзины: {e}")
        await update.message.reply_text("Произошла ошибка при загрузке корзины.")


# ======= Оформление заказа =======
async def checkout(update: Update, context: CallbackContext):
    """
    Оформление заказа из корзины пользователя.
    """
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        # Получаем корзину пользователя
        cart = await sync_to_async(Cart.objects.get)(user__telegram_id=user.id)
        cart_items = await sync_to_async(lambda: list(cart.items.all()))()

        if not cart_items:
            await query.message.reply_text("\U0001F6D2 Корзина пуста. Невозможно оформить заказ.")
            return

        # Создаем заказ (синхронная функция для sync_to_async)
        def create_order():
            # Вычисляем общую стоимость заказа
            total_price = sum(item.product.price * item.quantity for item in cart_items)

            # Создаём заказ с указанной стоимостью
            order = Order.objects.create(
                user=cart.user,
                status="Новый",
                total_price=total_price  # Указываем вычисленное значение
            )

            # Добавляем позиции заказа
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.price
                )

            return order

        # Асинхронно вызываем синхронную функцию
        order = await sync_to_async(create_order)()

        # Очищаем корзину
        await sync_to_async(cart.items.all().delete)()

        logger.info(f"Пользователь {user.username} ({user.id}) оформил заказ #{order.id}.")
        await query.message.reply_text(f"✅ Ваш заказ #{order.id} успешно оформлен!")

    except Cart.DoesNotExist:
        await query.message.reply_text("\U0001F6D2 Корзина пуста. Невозможно оформить заказ.")
    except Exception as e:
        logger.exception(f"Ошибка при оформлении заказа: {e}")
        await query.message.reply_text("Произошла ошибка при оформлении заказа.")

# ======= Просмотр заказов =======
async def view_orders(update: Update, context: CallbackContext):
    """
    Отображение истории заказов пользователя в виде таблицы.
    """
    user = update.effective_user

    try:
        logger.info(f"Пользователь {user.username} ({user.id}) вызвал команду /view_orders")

        # Получаем заказы пользователя
        orders = await sync_to_async(lambda: list(Order.objects.filter(user__telegram_id=user.id)))()
        if not orders:
            await update.message.reply_text("У вас нет оформленных заказов.")
            return

        # Формируем таблицу с заказами
        table_text = ""
        for order in orders:
            table_text += f"\n<b>Заказ №{order.id}</b>\n"
            table_text += f"{'Товар':<20} {'Кол-во':<10} {'Цена':<10} {'Статус':<15}\n"
            items = await sync_to_async(lambda: list(order.items.all()))()
            for item in items:
                product_name = await sync_to_async(lambda: item.product.name)()
                table_text += f"{product_name:<20} {item.quantity:<10} {item.price:<10.2f} {order.status:<15}\n"

        # Разбиваем текст на части, если он слишком длинный
        chunks = [table_text[i:i + 4000] for i in range(0, len(table_text), 4000)]
        for chunk in chunks:
            await update.message.reply_text(f"<pre>{chunk}</pre>", parse_mode="HTML")

    except Exception as e:
        logger.exception(f"Ошибка при отображении заказов для пользователя {user.username} ({user.id}): {e}")
        await update.message.reply_text("Произошла ошибка при загрузке истории заказов.")
