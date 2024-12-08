from django.urls import path
from . import views

app_name = 'admin_zone'

urlpatterns = [
    path('', views.admin_home, name='home'),  # Главная страница админ-зоны
    path('orders/', views.manage_orders, name='orders'),  # Управление заказами
    path('orders/<int:order_id>/update_status/', views.update_order_status, name='update_order_status'),  # Обновление статуса заказа
    path('reviews/', views.manage_reviews, name='reviews'),  # Управление отзывами
    path('reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),  # Удаление отзыва
    path('analytics/', views.view_analytics, name='analytics'),  # Просмотр аналитики
]
