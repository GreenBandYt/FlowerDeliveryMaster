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
    cart_items = cart.cartitem_set.all()  # Получаем все товары в корзине
    return render(request, 'catalog/cart.html', {'cart': cart, 'cart_items': cart_items})

def add_to_cart(request, product_id):
    """
    Добавление товара в корзину.
    """
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)  # Получаем или создаём корзину пользователя

    # Проверяем, есть ли товар в корзине
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1  # Если товар уже в корзине, увеличиваем количество
    cart_item.save()

    return redirect('catalog:cart')  # Перенаправляем на страницу корзины
