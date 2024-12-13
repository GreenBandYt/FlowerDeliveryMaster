from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # Импортируем наше представление для регистрации и новой страницы

urlpatterns = [
    # Login маршрут
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    # Logout маршрут с перенаправлением на login
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    # Маршрут для регистрации
    path('register/', views.register, name='register'),
    # Новый маршрут для страницы с информацией о Telegram-боте
    path('telegram-info/', views.telegram_info, name='telegram_info'),
]
