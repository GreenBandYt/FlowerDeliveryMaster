from django.shortcuts import render, get_object_or_404
from .models import Product

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
