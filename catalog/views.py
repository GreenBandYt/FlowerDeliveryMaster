from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cart, CartItem

def catalog_home(request):
    """
    Главная страница каталога с отображением всех товаров.
    """
    products = Product.objects.all()  # Получаем все товары из базы данных
    return render(request, 'catalog/home.html', {'products': products})

def product_detail(request, product_id):
    """
    Страница деталей товара.
    """
    product = get_object_or_404(Product, id=product_id)  # Получаем товар или возвращаем 404
    return render(request, 'catalog/product_detail.html', {'product': product})

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
