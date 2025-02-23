# bot/handlers/customer.py

import os
from PIL import Image
from telegram.constants import ParseMode  # Для HTML-разметки сообщений
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes
from asgiref.sync import sync_to_async
from prettytable import PrettyTable
from catalog.models import Product, Cart, CartItem, Order, OrderItem
import logging
from users.models import CustomUser
from bot.keyboards.customer_keyboards import customer_keyboard
# from bot.handlers.customer import view_orders, view_cart, view_catalog, help
# from bot.handlers.admin import analytics, manage_users, orders

from telegram.constants import ParseMode
from PIL import Image
from textwrap import shorten
from bot.utils.time_utils import is_working_hours


# Настройка логгера
logger = logging.getLogger(__name__)

async def customer_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Приветствие клиента.
    Устанавливает состояние 'customer_start' и роль 'customer', затем отправляет сообщение с клавиатурой.
    """
    telegram_id = update.effective_user.id
    logger.info(f"[CUSTOMER_START] Запуск для пользователя {telegram_id}")

    # Устанавливаем роль и состояние клиента
    context.user_data["role"] = "customer"
    context.user_data["state"] = "customer_start"

    # Получаем пользователя из базы
    user = await sync_to_async(CustomUser.objects.filter(telegram_id=telegram_id).first)()

    if not user:
        logger.error(f"[CUSTOMER_START ERROR] Пользователь {telegram_id} не найден в БД!")
        await update.message.reply_text("❌ Ошибка: Ваш аккаунт не найден. Попробуйте снова или обратитесь в поддержку.")
        return

    # Отправляем сообщение с клавиатурой
    await update.message.reply_text(
        f"🌸 Здравствуйте, {user.username}!\n"
        "🎉 Доступные функции:\n"
        "📦 Мои заказы\n"
        "🛒 Корзина\n"
        "🛍️ Каталог\n"
        "ℹ️ Показать помощь",
        reply_markup=customer_keyboard
    )

    logger.info(f"[CUSTOMER_START] Приветственное сообщение отправлено пользователю {telegram_id}")

async def handle_customer_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Вывод справочной информации для клиента.
    """
    telegram_id = update.effective_user.id
    logger.info(f"[CUSTOMER_HELP] Пользователь {telegram_id} запросил помощь.")

    await update.message.reply_text(
        "ℹ️ *Клиентская помощь:*\n\n"
        "📦 *Мои заказы* - Посмотреть текущие и завершённые заказы.\n"
        "🛒 *Корзина* - Проверить товары перед оформлением.\n"
        "🛍️ *Каталог* - Выбрать цветы и букеты для заказа.\n"
        "ℹ️ *Показать помощь* - Показать данный текст!",
        parse_mode="Markdown"
    )


# ======= Просмотр каталога товаров =======
# Функция уменьшения изображения
def customer_resize_image(image_path, max_size=(512, 512)):
    """
    Уменьшает изображение до max_size и сохраняет в /tmp/, чтобы не изменять оригинальный файл.
    """
    try:
        with Image.open(image_path) as img:
            img.thumbnail(max_size)

            # Создаём временный файл в /tmp/
            resized_path = f"/tmp/{os.path.basename(image_path)}_resized.jpg"
            img.save(resized_path, "JPEG")

            return resized_path
    except Exception as e:
        logger.error(f"❌ Ошибка при обработке изображения {image_path}: {e}")
        return image_path  # Возвращаем оригинальный путь, если уменьшение не удалось

async def handle_customer_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отображение списка товаров с инлайн-кнопками для добавления в корзину.
    """
    telegram_id = update.effective_user.id
    logger.info(f"[CUSTOMER_CATALOG] Пользователь {telegram_id} запросил каталог товаров.")

    try:
        # Получаем список товаров из базы
        products = await sync_to_async(lambda: list(Product.objects.all()))()

        if not products:
            await update.message.reply_text("📭 Каталог пока пуст. Загляните позже!")
            return

        # Обрабатываем товары один за другим
        for product in products:
            text = (
                f"📦 *{product.name}*\n"
                f"💰 Цена: *{product.price:.2f}* руб.\n"
                f"ℹ️ {product.description}"
            )

            # Проверяем изображение
            image_path = os.path.join("media", str(product.image))

            if os.path.exists(image_path):
                resized_image_path = customer_resize_image(image_path)

                # Формируем инлайн-кнопку для добавления в корзину
                keyboard = [[InlineKeyboardButton(
                    "➕ Добавить в корзину",
                    callback_data=f"add_to_cart_{product.id}"
                )]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                # Отправляем фото, текст и кнопку
                await context.bot.send_photo(
                    chat_id=update.message.chat_id,
                    photo=open(resized_image_path, "rb"),
                    caption=text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )

                # Удаляем временный уменьшенный файл, если он создавался
                if resized_image_path.startswith("/tmp/") and os.path.exists(resized_image_path):
                    os.remove(resized_image_path)
            else:
                logger.warning(f"[CUSTOMER_CATALOG] Изображение {image_path} не найдено.")
                await update.message.reply_text(f"{text}\n\n❌ *Изображение недоступно.*", parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        logger.exception(f"[CUSTOMER_CATALOG] Ошибка при загрузке каталога для пользователя {telegram_id}: {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при загрузке каталога. Попробуйте позже.")


# ======= Обработка добавления товара в корзину =======
async def customer_add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Добавление товара в корзину пользователя по callback-запросу.
    """
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()
        product_id = int(query.data.split('_')[-1])

        # Получаем пользователя
        db_user = await sync_to_async(CustomUser.objects.get)(telegram_id=user.id)

        # Получаем товар из базы данных
        product = await sync_to_async(Product.objects.get)(id=product_id)

        # Получаем или создаем корзину пользователя
        cart, _ = await sync_to_async(Cart.objects.get_or_create)(user=db_user)

        # Проверяем, есть ли товар уже в корзине
        cart_item, created = await sync_to_async(CartItem.objects.get_or_create)(
            cart=cart, product=product,
            defaults={"quantity": 1, "price": product.price}
        )

        if not created:
            # Ограничиваем количество товара (например, максимум 10 шт.)
            if cart_item.quantity >= 10:
                await query.message.reply_text("⚠️ Максимальное количество этого товара уже в корзине!")
                return

            cart_item.quantity += 1
            cart_item.price = cart_item.quantity * product.price
            await sync_to_async(cart_item.save)()

        logger.info(f"Товар {product.name} добавлен в корзину пользователя {user.username} ({user.id}).")

        # Обновляем inline-кнопку
        keyboard = [[InlineKeyboardButton("✅ Уже в корзине", callback_data="none")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_reply_markup(reply_markup=reply_markup)
        await query.message.reply_text(f"\U0001F4E6 Товар '{product.name}' добавлен в вашу корзину!")

    except CustomUser.DoesNotExist:
        logger.error(f"❌ Пользователь с ID {user.id} не найден в БД.")
        await query.message.reply_text("⚠️ Ошибка: пользователь не найден.")
    except Product.DoesNotExist:
        logger.error(f"❌ Товар с ID {product_id} не найден.")
        await query.message.reply_text("⚠️ Ошибка: товар не найден.")
    except Exception as e:
        logger.exception(f"❌ Ошибка при добавлении товара в корзину: {e}")
        await query.message.reply_text("⚠️ Произошла ошибка при добавлении товара в корзину.")



# ======= Просмотр корзины =======
async def customer_view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отображение содержимого корзины в формате карточек (без фото) с проверкой рабочего времени.
    """
    user = update.effective_user
    message = update.callback_query.message if update.callback_query else update.message

    try:
        logger.info(f"🛒 Пользователь {user.username} ({user.id}) открыл корзину.")

        # Проверяем, есть ли корзина у пользователя
        cart_exists = await sync_to_async(Cart.objects.filter(user__telegram_id=user.id).exists)()
        if not cart_exists:
            await message.reply_text("🛒 Ваша корзина пуста.")
            return

        # Получаем содержимое корзины
        cart_items = await sync_to_async(
            lambda: list(CartItem.objects.filter(cart__user__telegram_id=user.id).select_related('product'))
        )()

        if not cart_items:
            await message.reply_text("🛒 Ваша корзина пуста.")
            return

        total_price = 0

        for item in cart_items:
            product = item.product
            total_price += item.price

            text = (
                f"📦 <b>{product.name}</b>\n"
                f"Количество: <b>{item.quantity}</b>\n"
                f"Цена: <b>{item.price} ₽</b>"
            )

            # Кнопки управления товаром
            keyboard = [
                [
                    InlineKeyboardButton("➖", callback_data=f"decrease_{product.id}"),
                    InlineKeyboardButton(f"{item.quantity} шт.", callback_data="ignore"),
                    InlineKeyboardButton("➕", callback_data=f"increase_{product.id}")
                ],
                [InlineKeyboardButton("❌ Удалить", callback_data=f"remove_from_cart_{product.id}")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            # Отправляем карточку товара (без фото)
            await message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)

        # Проверяем рабочее время
        is_working_time = await sync_to_async(is_working_hours)()


        # Если сейчас рабочее время, показываем кнопку оформления заказа
        if is_working_time:
            checkout_markup = InlineKeyboardMarkup([[InlineKeyboardButton("📝 Оформить заказ", callback_data="checkout")]])
            await message.reply_text(f"💰 <b>Итого: {total_price} ₽</b>", parse_mode="HTML", reply_markup=checkout_markup)
        else:
            await message.reply_text(f"💰 <b>Итого: {total_price} ₽</b>\n\n❌ Сейчас нерабочее время. Заказы принимаются с 09:00 до 18:00.", parse_mode="HTML")

    except Exception as e:
        logger.exception(f"❌ Ошибка при просмотре корзины: {e}")
        await message.reply_text("❌ Произошла ошибка при загрузке корзины.")

# ======= Уменьшение количества товара в корзине =======
async def customer_decrease_quantity(update: Update, context: CallbackContext):
    """
    Уменьшение количества товара в корзине.
    """
    query = update.callback_query
    user = update.effective_user

    try:
        product_id = int(query.data.split("_")[1])

        # Получаем запись товара в корзине
        cart_item = await sync_to_async(
            lambda: CartItem.objects.filter(cart__user__telegram_id=user.id, product_id=product_id).select_related('product').first()
        )()

        if not cart_item:
            await query.answer("❌ Товар не найден в вашей корзине.")
            return

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.price = cart_item.quantity * cart_item.product.price  # Нет необходимости использовать sync_to_async
            await sync_to_async(cart_item.save)()
            await query.answer(f"✅ Количество товара уменьшено до {cart_item.quantity}.")
        else:
            await query.answer("❌ Невозможно уменьшить количество ниже 1.")

        # Обновляем корзину
        await customer_view_cart(update, context)

    except Exception as e:
        logger.exception(f"❌ Ошибка при уменьшении количества товара: {e}")
        await query.answer("❌ Произошла ошибка при изменении количества.")

# ======= Увеличение количества товара в корзине =======
async def customer_increase_quantity(update: Update, context: CallbackContext):
    """
    Увеличение количества товара в корзине.
    """
    query = update.callback_query
    user = query.from_user

    try:
        product_id = int(query.data.split("_")[-1])

        # Получаем товар в корзине
        cart_item = await sync_to_async(
            lambda: CartItem.objects.filter(cart__user__telegram_id=user.id, product_id=product_id).select_related(
                'product').first()
        )()

        if not cart_item:
            await query.answer("⚠️ Товар не найден в вашей корзине.")
            return

        # Увеличиваем количество
        cart_item.quantity += 1
        cart_item.price = cart_item.quantity * cart_item.product.price  # Без использования sync_to_async
        await sync_to_async(cart_item.save)()

        await query.answer(f"✅ Количество товара '{cart_item.product.name}' увеличено до {cart_item.quantity}.")

        # Обновляем корзину
        await customer_view_cart(update, context)

    except Exception as e:
        logger.exception(f"❌ Ошибка при увеличении количества товара {product_id}: {e}")
        await query.answer("❌ Произошла ошибка при увеличении количества товара.")

# ======= Удаление товара из корзины =======
async def customer_remove_from_cart(update: Update, context: CallbackContext):
    """
    Удаление товара из корзины пользователя по callback-запросу.
    """
    query = update.callback_query
    user = query.from_user

    try:
        product_id = int(query.data.split("_")[-1])

        # Получаем товар в корзине
        cart_item = await sync_to_async(
            lambda: CartItem.objects.filter(cart__user__telegram_id=user.id, product_id=product_id).select_related('product').first()
        )()

        if not cart_item:
            await query.answer("❌ Товар не найден в вашей корзине.")
            return

        product_name = await sync_to_async(lambda: cart_item.product.name)()  # Получаем название товара перед удалением

        await sync_to_async(cart_item.delete)()
        await query.answer(f"✅ Товар '{product_name}' удалён из корзины.")

        # Обновляем корзину
        await customer_view_cart(update, context)

    except Exception as e:
        logger.exception(f"Ошибка при удалении товара: {e}")
        await query.answer("❌ Произошла ошибка при удалении товара.")

# ======= Вывод заказа для подтверждения оформления =======
async def customer_view_checkout(update: Update, context: CallbackContext):
    """
    Функция вывода заказа для подтверждения оформления:
    - Проверка рабочего времени
    - Вывод информации
    - Кнопки "Подтвердить", "Отменить", "Выход"
    """
    query = update.callback_query
    user = update.effective_user

    try:
        await query.answer()

        # ✅ Проверяем рабочее время ТОЧНО КАК В `customer_view_cart`
        is_working_time = await sync_to_async(is_working_hours)()
        if not is_working_time:
            await query.message.reply_text("⏳ Сейчас нерабочее время. Заказы принимаются с 09:00 до 18:00.")
            return

        # ✅ Получаем пользователя
        db_user = await sync_to_async(lambda: CustomUser.objects.get(telegram_id=user.id))()

        # ✅ Получаем корзину (через `sync_to_async`)
        cart_items = await sync_to_async(lambda: list(
            CartItem.objects.filter(cart__user=db_user).select_related('product').all()
        ))()

        if not cart_items:
            await query.message.reply_text("🛒 Ваша корзина пуста.")
            return

        # ✅ Считаем итоговую сумму
        total_price = sum(item.price * item.quantity for item in cart_items)

        # ✅ Формируем список товаров
        items_text = "\n".join(
            [f"📦 {item.product.name} - {item.quantity} шт." for item in cart_items]
        )

        # ✅ Выводим информацию пользователю
        message_text = (
            f"📝 Оформление заказа:\n\n"
            f"👤 Покупатель: {db_user.username}\n"
            f"📞 Телефон: {db_user.phone_number}\n"
            f"📍 Адрес: {db_user.address}\n\n"
            f"{items_text}\n"
            f"💰 Итого: {total_price} ₽"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Подтвердить Заказ", callback_data="confirm_order")],
            [InlineKeyboardButton("❌ Отменить Заказ", callback_data="cancel_order")],

        ])

        await query.message.reply_text(message_text, reply_markup=keyboard)

    except Exception as e:
        await query.message.reply_text("❌ Ошибка при оформлении заказа.")
        print(f"Ошибка: {e}")

# ======= Подтверждение оформления заказа из корзины =======
async def customer_confirm_checkout(update: Update, context: CallbackContext):
    """
    Создание заказа и очистка корзины после подтверждения.
    """
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        # Получаем пользователя
        db_user = await sync_to_async(CustomUser.objects.get)(telegram_id=user.id)

        # Получаем корзину пользователя
        cart = await sync_to_async(lambda: Cart.objects.get(user=db_user))()

        # Проверяем, есть ли товары в корзине
        cart_items = await sync_to_async(lambda: list(cart.items.all()))()

        if not cart_items:
            await query.message.reply_text("🛒 Ваша корзина пуста.")
            return

        # Создаём заказ
        order = await sync_to_async(Order.objects.create)(
            user=db_user,
            total_price=sum(item.price for item in cart_items),
            address=db_user.address  # Записываем адрес пользователя
        )

        # Переносим товары из корзины в заказ
        for item in cart_items:
            product = await sync_to_async(lambda: item.product)()  # Обернули product в sync_to_async
            await sync_to_async(OrderItem.objects.create)(
                order=order,
                product=product,
                quantity=item.quantity,
                price=item.price
            )

        # Очищаем корзину пользователя
        await sync_to_async(lambda: cart.items.all().delete())()

        # Убираем кнопки у сообщения
        await query.edit_message_reply_markup(reply_markup=None)


        # Отправляем уведомления админам и сотрудникам
        # await notify_admin(order)
        # await notify_staff(order)


        # Сообщаем пользователю об успешном оформлении заказа
        logger.info(f"✅ Пользователь {user.username} ({user.id}) оформил заказ #{order.id}.")
        await query.message.reply_text(f"\U0001F4E6 Ваш заказ #{order.id} успешно оформлен!")

    except Cart.DoesNotExist:
        logger.error(f"❌ Корзина пользователя {user.username} ({user.id}) не найдена.")
        await query.message.reply_text("⚠️ Ошибка: корзина не найдена.")
    except Exception as e:
        logger.exception(f"❌ Ошибка при подтверждении оформления заказа: {e}")
        await query.message.reply_text("⚠️ Произошла ошибка при оформлении заказа.")


# ======= Отмена заказа =======
async def customer_cancel_order(update: Update, context: CallbackContext):
    """
    Отмена заказа пользователем.
    """
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()

        # Получаем пользователя
        db_user = await sync_to_async(CustomUser.objects.get)(telegram_id=user.id)

        # Ищем последний заказ пользователя в статусе "created"
        order = await sync_to_async(lambda: Order.objects.filter(user=db_user, status="created").last())()

        if not order:
            await query.message.reply_text("⚠️ У вас нет активных заказов, которые можно отменить.")
            return

        # Обновляем статус заказа на "canceled"
        order.status = "canceled"
        await sync_to_async(order.save)()

        # Уведомляем пользователя
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(f"❌ Ваш заказ #{order.id} был отменён.")

        # Логируем отмену
        logger.info(f"❌ Пользователь {user.username} ({user.id}) отменил заказ #{order.id}.")

    except CustomUser.DoesNotExist:
        logger.error(f"❌ Пользователь {user.username} ({user.id}) не найден в БД.")
        await query.message.reply_text("⚠️ Ошибка: пользователь не найден.")
    except Exception as e:
        logger.exception(f"❌ Ошибка при отмене заказа: {e}")
        await query.message.reply_text("⚠️ Произошла ошибка при отмене заказа.")





# ======= Просмотр заказов =======
async def customer_view_orders(update: Update, context: CallbackContext):
    """
    Отображение истории заказов пользователя с возможностью повторного заказа.
    """
    user = update.effective_user

    try:
        logger.info(f"Пользователь {user.username} ({user.id}) открыл список заказов.")

        # Получаем заказы пользователя
        orders = await sync_to_async(lambda: list(Order.objects.filter(user__telegram_id=user.id)))()
        if not orders:
            await update.message.reply_text("У вас нет оформленных заказов.")
            return

        # Формируем сообщения с заказами
        for order in orders:
            order_text = f"\n<b>📦 Заказ №{order.id}</b>\n"
            order_text += f"🗓 Дата: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            order_text += f"💰 Сумма: {order.total_price:.2f} ₽\n"
            order_text += f"📌 Статус: <b>{order.get_status_display()}</b>\n"
            order_text += f"📜 Товары:\n"

            # Получаем товары в заказе
            items = await sync_to_async(lambda: list(order.items.all()))()
            for item in items:
                product_name = await sync_to_async(lambda: item.product.name)()
                order_text += f"  ➜ {shorten(product_name, width=30, placeholder='...')} — {item.quantity} шт. ({item.price:.2f} ₽)\n"

            # Добавляем кнопку "Повторить заказ"
            keyboard = [[InlineKeyboardButton("🔄 Повторить заказ", callback_data=f"repeat_order_{order.id}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(order_text, parse_mode="HTML", reply_markup=reply_markup)

    except Exception as e:
        logger.exception(f"Ошибка при отображении заказов для пользователя {user.username} ({user.id}): {e}")
        await update.message.reply_text("⚠️ Произошла ошибка при загрузке истории заказов.")


async def customer_repeat_order(update: Update, context: CallbackContext):
    """
    Повторение заказа: копирование товаров из заказа в корзину пользователя.
    """
    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()
        order_id = int(query.data.split('_')[-1])

        # Получаем пользователя
        db_user = await sync_to_async(CustomUser.objects.get)(telegram_id=user.id)

        # Получаем заказ
        order = await sync_to_async(Order.objects.get)(id=order_id, user=db_user)

        # Получаем или создаем корзину пользователя
        cart, _ = await sync_to_async(Cart.objects.get_or_create)(user=db_user)

        # Переносим товары из заказа в корзину
        order_items = await sync_to_async(lambda: list(order.items.all()))()
        for item in order_items:
            product = await sync_to_async(lambda: item.product)()

            # Проверяем, есть ли товар уже в корзине
            cart_item, created = await sync_to_async(CartItem.objects.get_or_create)(
                cart=cart, product=product,
                defaults={"quantity": item.quantity, "price": item.price}
            )

            if not created:
                cart_item.quantity += item.quantity
                cart_item.price = cart_item.quantity * product.price
                await sync_to_async(cart_item.save)()

        await query.message.reply_text(f"✅ Все товары из заказа #{order_id} добавлены в корзину!")

    except Order.DoesNotExist:
        await query.message.reply_text("⚠️ Ошибка: заказ не найден.")
    except CustomUser.DoesNotExist:
        await query.message.reply_text("⚠️ Ошибка: пользователь не найден.")
    except Exception as e:
        logger.exception(f"❌ Ошибка при повторении заказа #{order_id}: {e}")
        await query.message.reply_text("⚠️ Произошла ошибка при повторении заказа.")



#
# # ======= Просмотр заказов =======
# async def customer_view_orders(update: Update, context: CallbackContext):
#     """
#     Отображение истории заказов пользователя в виде таблицы.
#     """
#     user = update.effective_user
#
#     try:
#         logger.info(f"Пользователь {user.username} ({user.id}) вызвал команду /view_orders")
#
#         # Получаем заказы пользователя
#         orders = await sync_to_async(lambda: list(Order.objects.filter(user__telegram_id=user.id)))()
#         if not orders:
#             await update.message.reply_text("У вас нет оформленных заказов.")
#             return
#
#         # Формируем таблицу с заказами
#         table_text = ""
#         for order in orders:
#             table_text += f"\n<b>Заказ №{order.id}</b>\n"
#             table_text += f"{'Товар':<20} {'Кол-во':<10} {'Цена':<10} {'Статус':<15}\n"
#             items = await sync_to_async(lambda: list(order.items.all()))()
#             for item in items:
#                 product_name = await sync_to_async(lambda: item.product.name)()
#                 table_text += f"{product_name:<20} {item.quantity:<10} {item.price:<10.2f} {order.status:<15}\n"
#
#         # Разбиваем текст на части, если он слишком длинный
#         chunks = [table_text[i:i + 4000] for i in range(0, len(table_text), 4000)]
#         for chunk in chunks:
#             await update.message.reply_text(f"<pre>{chunk}</pre>", parse_mode="HTML")
#
#     except Exception as e:
#         logger.exception(f"Ошибка при отображении заказов для пользователя {user.username} ({user.id}): {e}")
#         await update.message.reply_text("Произошла ошибка при загрузке истории заказов.")





# ==========================================

# ======= Просмотр текущих заказов =======
# async def handle_staff_my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """
#     Отображение заказов сотрудника (которые он выполняет).
#     """
#     telegram_id = update.effective_user.id
#     try:
#         # ✅ Получаем сотрудника
#         user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id, is_staff=True)
#         logger.info(f"[STAFF] Пользователь {telegram_id} запросил список своих заказов в работе.")
#
#         # ✅ Фильтруем заказы, где сотрудник - исполнитель
#         orders = await sync_to_async(lambda: list(Order.objects.filter(status="processing", executor_id=user.id)))()
#
#         if not orders:
#             logger.warning(f"❌ У сотрудника {telegram_id} нет активных заказов.")
#             await update.message.reply_text("❌ У вас нет активных заказов в работе.")
#             return ConversationHandler.END
#
#         # ✅ Формируем список заказов с кнопками "ℹ️ Подробнее"
#         for order in orders:
#             translated_status = STATUS_TRANSLATION.get(order.status, "Неизвестный статус")
#             message = (
#                 f"📦 <b>Заказ #{order.id}</b>\n"
#                 f"💰 Сумма: {order.total_price:.2f} ₽\n"
#                 f"📍 Адрес: {order.address or 'Не указан'}\n"
#                 f"📌 Статус: <b>{translated_status}</b>\n\n"
#             )
#
#             # ✅ Кнопка "ℹ️ Подробнее" (правильный callback_data)
#             keyboard = [[InlineKeyboardButton("ℹ️ Подробнее", callback_data=f"staff_order_details:{order.id}")]]
#             reply_markup = InlineKeyboardMarkup(keyboard)
#
#             await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
#
#         logger.info(f"✅ Отправлен список из {len(orders)} заказов в работе пользователю {telegram_id}.")
#         return ConversationHandler.END
#
#     except CustomUser.DoesNotExist:
#         logger.error(f"❌ Ошибка: сотрудник с Telegram ID {telegram_id} не найден.")
#         await update.message.reply_text("❌ У вас нет прав для выполнения этой команды.")
#         return ConversationHandler.END
#
#     except Exception as e:
#         logger.error(f"❌ Ошибка в handle_staff_my_orders: {e}", exc_info=True)
#         await update.message.reply_text("❌ Произошла ошибка. Попробуйте позже.")
#         return ConversationHandler.END
#
#
# # ======= Детали заказа =======
#
# # Функция для уменьшения размера изображения перед отправкой
# def resize_image(image_path, max_size=(512, 512)):
#     try:
#         with Image.open(image_path) as img:
#             img.thumbnail(max_size)  # Уменьшение изображения до максимального размера
#             new_path = f"{image_path}_resized.jpg"
#             img.save(new_path, "JPEG")
#             return new_path
#     except Exception as e:
#         logger.error(f"Ошибка при изменении размера изображения {image_path}: {e}")
#         return image_path
#
# import os
# from django.conf import settings
#
# async def handle_staff_order_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     query = update.callback_query
#     await query.answer()
#
#     telegram_id = update.effective_user.id
#     callback_data = query.data
#
#     parts = callback_data.split(":")
#     if len(parts) != 2 or parts[0] != "staff_order_details":
#         logger.warning(f"❌ Некорректный callback_data: {callback_data}")
#         return
#
#     order_id = int(parts[1])
#
#     try:
#         user = await sync_to_async(CustomUser.objects.get)(telegram_id=telegram_id, is_staff=True)
#         order = await sync_to_async(Order.objects.select_related("user").get)(
#             id=order_id, executor_id=user.id, status="processing"
#         )
#         order_items = await sync_to_async(lambda: list(order.items.select_related("product").all()))()
#
#         details = (
#             f"📦 <b>Заказ #{order.id}</b>\n"
#             f"👤 <b>Заказчик:</b> {order.user.first_name} {order.user.last_name}\n"
#             f"📞 <b>Телефон:</b> {order.user.phone_number}\n"
#             f"💰 <b>Сумма:</b> {order.total_price:.2f} ₽\n"
#             f"📍 <b>Адрес:</b> {order.address or 'Не указан'}\n"
#             f"📌 <b>Статус:</b> В процессе\n\n"
#             f"🛍 <b>Товары:</b>\n"
#         )
#
#         has_images = False
#
#         for item in order_items:
#             details += f"🔹 {item.product.name} — {item.quantity} шт. по {item.price:.2f} ₽\n"
#             if item.product.image:
#                 has_images = True
#
#         await query.edit_message_text(details, parse_mode="HTML")
#
#         if has_images:
#             for item in order_items:
#                 if item.product.image:
#                     image_relative_path = str(item.product.image)
#                     image_absolute_path = os.path.join(settings.MEDIA_ROOT, image_relative_path)
#
#                     if not os.path.exists(image_absolute_path):
#                         logger.warning(f"❌ Файл изображения не найден: {image_absolute_path}")
#                         continue
#
#                     try:
#                         resized_image_path = resize_image(image_absolute_path)
#
#                         with open(resized_image_path, "rb") as photo:
#                             caption_text = f"🌸 {item.product.name} — {item.quantity} шт. по {item.price:.2f} ₽"
#                             await context.bot.send_photo(
#                                 chat_id=telegram_id,
#                                 photo=photo,
#                                 caption=caption_text,
#                                 parse_mode="HTML"
#                             )
#                             logger.info(f"✅ Фото отправлено: {resized_image_path}")
#
#                         if resized_image_path != image_absolute_path:
#                             os.remove(resized_image_path)
#
#                     except Exception as e:
#                         logger.error(f"❌ Ошибка при отправке фото {image_absolute_path}: {e}")
#
#     except Order.DoesNotExist:
#         await query.edit_message_text("❌ Заказ не найден или уже закрыт.")
#     except Exception as e:
#         logger.error(f"❌ Ошибка в handle_staff_order_details: {e}")
#         await query.edit_message_text("❌ Произошла ошибка. Попробуйте позже.")
