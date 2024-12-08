from django.shortcuts import render, get_object_or_404, redirect
from users.models import CustomUser  # Импортируем модель пользователя
from catalog.models import Order, OrderItem  # Импортируем модели заказов и элементов заказов
from django.db.models import Sum, Avg  # Для аналитических вычислений
from django.contrib import messages  # Для отображения уведомлений


# Функция для отображения главной страницы админ-зоны
def admin_home(request):
    users = CustomUser.objects.all()  # Получаем всех пользователей
    return render(request, 'admin_zone/admin_dashboard.html', {
        'users': users,  # Передаем список пользователей в шаблон
    })


# Функция для управления заказами
def manage_orders(request):
    """
    Представление для управления заказами.
    """
    orders = Order.objects.all()  # Получаем заказы из правильной таблицы
    return render(request, 'admin_zone/manage_orders.html', {
        'orders': orders  # Передаем заказы в шаблон
    })

# Функция для обновления статуса заказа
def update_order_status(request, order_id):
    """
    Обновление статуса заказа.
    """
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            messages.success(request, f"Статус заказа #{order.id} успешно обновлен на '{new_status}'.")
        else:
            messages.error(request, "Ошибка: статус заказа не указан.")
    return redirect('admin_zone:orders')


# Функция для управления отзывами
def manage_reviews(request):
    """
    Представление для управления отзывами.
    """
    return render(request, 'admin_zone/manage_reviews.html')  # Указываем конкретный путь к шаблону


# Функция для просмотра аналитики
def view_analytics(request):
    """
    Представление для просмотра аналитики.
    """
    # Подсчет общего количества заказов
    total_orders = Order.objects.count()

    # Подсчет общей выручки
    total_revenue = OrderItem.objects.aggregate(total_revenue=Sum('price'))['total_revenue']

    # Подсчет количества пользователей
    total_users = CustomUser.objects.count()

    # Подсчет среднего чека
    average_order_value = Order.objects.aggregate(avg_order=Avg('total_price'))['avg_order']

    # Передача данных в шаблон
    return render(request, 'admin_zone/view_analytics.html', {
        'total_orders': total_orders,
        'total_revenue': total_revenue or 0,  # Если нет данных, показываем 0
        'total_users': total_users,
        'average_order_value': round(average_order_value or 0, 2)  # Округляем до 2 знаков
    })
