from django.contrib import admin  # Добавляем этот импорт
from django.urls import path, include
from flowerdelivery.views import home_redirect

urlpatterns = [
    path('', home_redirect, name='home'),  # Редирект на login или catalog
    path('admin/', admin.site.urls),  # Административная панель
    path('users/', include('users.urls')),  # Пользовательские маршруты
    path('catalog/', include('catalog.urls', namespace='catalog')),  # Пространство имен для каталога
]
