from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from flowerdelivery.views import home_redirect

urlpatterns = [
    path('', home_redirect, name='home'),  # Редирект на login или catalog
    path('admin/', admin.site.urls),  # Административная панель
    path('users/', include('users.urls')),  # Пользовательские маршруты
    path('catalog/', include('catalog.urls', namespace='catalog')),  # Пространство имен для каталога
    path('admin-zone/', include('admin_zone.urls', namespace='admin_zone')),  # Пространство имен для admin_zone
]

# Добавляем маршруты для медиафайлов
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
