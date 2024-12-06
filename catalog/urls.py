from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog_home, name='home'),  # Главная страница каталога
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),  # Страница деталей товара
    path('cart/', views.cart_view, name='cart'),  # Страница корзины
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  # Добавление товара в корзину
]
