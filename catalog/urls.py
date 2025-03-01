# catalog/urls.py

from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog_home, name='home'),  # Главная страница каталога
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),  # Страница деталей товара
    path('product/<int:product_id>/reviews/', views.product_reviews, name='reviews'),  # Страница просмотра отзывов
    path('cart/', views.cart_view, name='cart'),  # Страница корзины
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  # Добавление товара в корзину
    path('update_quantity/<int:item_id>/', views.update_quantity, name='update_quantity'),  # Обновление количества товара
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),  # Удаление товара из корзины
    path('checkout/', views.checkout, name='checkout'),  # Оформление заказа
    path('order_history/', views.order_history, name='order_history'),  # История заказов
    path('repeat_order/<int:order_id>/', views.repeat_order, name='repeat_order'),  # Повторение заказа
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),  # Удаление заказа
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Маршрут для админ-зоны
]

