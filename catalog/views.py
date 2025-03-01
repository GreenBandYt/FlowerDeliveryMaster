from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cart, CartItem, Order, OrderItem, Review
from .forms import OrderForm, ReviewForm  # Импортируем формы
from django.contrib import messages
from django.core.paginator import Paginator  # Импортируем для пагинации
from django.contrib.auth.decorators import user_passes_test  # Для проверки прав

def catalog_home(request):
    """
    Главная страница каталога с отображением всех товаров.
    """
    products = Product.objects.all()  # Получаем все товары из базы данных
    return render(request, 'catalog/home.html', {'products': products})

def product_detail(request, product_id):
    """
    Страница деталей товара с возможностью добавления отзыва.
    """
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()  # Получаем все отзывы, связанные с этим товаром

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Создаём новый отзыв
            Review.objects.create(
                user=request.user,
                product=product,
                rating=form.cleaned_data['rating'],
                review_text=form.cleaned_data['review_text']
            )
            messages.success(request, "Ваш отзыв успешно добавлен!")
            return redirect('catalog:product_detail', product_id=product_id)
    else:
        form = ReviewForm()

    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form  # Передаём форму в шаблон
    })

def product_reviews(request, product_id):
    """
    Отображение всех отзывов для конкретного продукта с пагинацией.
    """
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by('-created_at')  # Сортируем отзывы по дате добавления
    paginator = Paginator(reviews, 5)  # Пагинация: 5 отзывов на страницу

    page_number = request.GET.get('page')
    page_reviews = paginator.get_page(page_number)

    return render(request, 'catalog/reviews.html', {
        'product': product,
        'reviews': page_reviews,
    })

def cart_view(request):
    """
    Отображение содержимого корзины.
    """
    cart, _ = Cart.objects.get_or_create(user=request.user)  # Получаем или создаём корзину пользователя
    cart_items = cart.items.all()  # Используем related_name для доступа к элементам
    return render(request, 'catalog/cart.html', {'cart': cart, 'cart_items': cart_items})

def add_to_cart(request, product_id):
    """
    Добавление товара в корзину.
    """
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)  # Получаем или создаём корзину пользователя

    # Получаем количество из формы (по умолчанию 1)
    quantity = int(request.POST.get('quantity', 1))

    # Проверяем, есть ли товар в корзине
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity  # Если товар уже в корзине, увеличиваем количество
    else:
        cart_item.quantity = quantity  # Устанавливаем новое количество для нового товара
    cart_item.save()

    return redirect('catalog:cart')  # Перенаправляем на страницу корзины

def update_quantity(request, item_id):
    """
    Обновление количества товара в корзине.
    """
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            cart_item.delete()  # Если количество становится 0, удаляем товар
    return redirect('catalog:cart')

def remove_from_cart(request, item_id):
    """
    Удаление товара из корзины.
    """
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        cart_item.delete()
    return redirect('catalog:cart')

def checkout(request):
    """
    Оформление заказа.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        messages.error(request, "Ваша корзина пуста. Добавьте товары перед оформлением заказа.")
        return redirect('catalog:cart')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Сохранение адреса в профиль пользователя, если изменён
            new_address = form.cleaned_data.get('address', '').strip()
            if new_address and new_address != getattr(request.user, 'address', ''):
                request.user.address = new_address
                request.user.save()

            # Создание нового заказа
            order = Order.objects.create(
                user=request.user,
                total_price=cart.get_total_price(),
                notes=form.cleaned_data.get('comments'),
                address=new_address,  # Сохранение адреса в заказе
            )

            # Перенос элементов из корзины в заказ
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.price
                )

            # Очищаем корзину после оформления заказа
            cart.items.all().delete()

            messages.success(request, "Ваш заказ успешно оформлен!")
            return redirect('catalog:home')
    else:
        # Подготовка данных для автозаполнения адреса
        initial_data = {
            'address': getattr(request.user, 'address', ''),  # Адрес пользователя
        }
        form = OrderForm(initial=initial_data)

    # Передача данных пользователя для отображения в шаблоне
    user_data = {
        'username': request.user.username,
        'phone': getattr(request.user, 'phone_number', 'Не указан'),  # Телефон пользователя
    }

    return render(request, 'catalog/checkout.html', {
        'cart_items': cart_items,
        'form': form,
        'user_data': user_data,
        'total_price': cart.get_total_price(),
    })

def order_history(request):
    """
    Отображение истории заказов пользователя.
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')  # Получаем заказы текущего пользователя
    return render(request, 'catalog/order_history.html', {'orders': orders})

def repeat_order(request, order_id):
    """
    Повторение заказа. Перенос всех товаров из указанного заказа в корзину.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)  # Убедимся, что заказ принадлежит пользователю
    cart, _ = Cart.objects.get_or_create(user=request.user)  # Получаем или создаём корзину пользователя

    for item in order.items.all():
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item.product)
        if not created:
            cart_item.quantity += item.quantity  # Если товар уже есть в корзине, увеличиваем количество
        else:
            cart_item.quantity = item.quantity  # Иначе добавляем как новый
        cart_item.save()

    messages.success(request, "Товары из заказа добавлены в вашу корзину.")
    return redirect('catalog:cart')

def delete_order(request, order_id):
    """
    Удаление заказа.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)  # Убедимся, что это заказ текущего пользователя
    if request.method == 'POST':
        order.delete()  # Удаляем заказ
        messages.success(request, f"Заказ {order_id} успешно удалён.")
    return redirect('catalog:order_history')  # Перенаправляем на историю заказов

@user_passes_test(lambda u: u.is_staff)  # Декоратор: доступ только для администраторов
def admin_dashboard(request):
    """
    Страница административной панели.
    """
    return render(request, 'catalog/admin_dashboard.html', {})  # Заглушка шаблона