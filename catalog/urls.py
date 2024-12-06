from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog_home, name='home'),  # Главная страница каталога
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),  # Страница деталей товара
]
