# admin_zone/views.py

from django.shortcuts import render, get_object_or_404, redirect
from users.models import CustomUser
from catalog.models import Order, OrderItem, Review
from django.db.models import Sum, Avg
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

# Функция для отображения главной страницы админ-зоны
def admin_home(request):
    users = CustomUser.objects.all()
    return render(request, 'admin_zone/admin_dashboard.html', {'users': users})


# Функция для управления заказами
def manage_orders(request):
    orders = Order.objects.all()
    return render(request, 'admin_zone/manage_orders.html', {'orders': orders})


# Функция для обновления статуса заказа
def update_order_status(request, order_id):
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
    reviews = Review.objects.all()
    return render(request, 'admin_zone/manage_reviews.html', {'reviews': reviews})


# Функция для удаления отзыва
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    messages.success(request, f"Отзыв #{review_id} успешно удален.")
    return redirect('admin_zone:reviews')


# Функция для просмотра аналитики
# Функция для просмотра аналитики
def view_analytics(request):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)
    year_start = today_start.replace(month=1, day=1)

    # Функция для подсчета данных по периодам
    def get_period_data(start_date):
        orders = Order.objects.filter(created_at__gte=start_date)
        users = CustomUser.objects.filter(date_joined__gte=start_date).count()
        revenue = OrderItem.objects.filter(order__created_at__gte=start_date).aggregate(Sum('price'))['price__sum'] or 0
        average_check = orders.aggregate(avg_check=Avg('total_price'))['avg_check'] or 0

        return {
            "users": users,
            "orders": orders.count(),
            "revenue": round(revenue, 2),
            "average_check": round(average_check, 2),
        }

    # Данные для каждого периода
    data_today = get_period_data(today_start)
    data_week = get_period_data(today_start - timedelta(days=7))
    data_month = get_period_data(month_start)
    data_year = get_period_data(year_start)

    # Общие данные за весь период
    total_orders = Order.objects.count()
    total_revenue = OrderItem.objects.aggregate(total_revenue=Sum('price'))['total_revenue'] or 0
    total_users = CustomUser.objects.count()
    average_order_value = Order.objects.aggregate(avg_order=Avg('total_price'))['avg_order'] or 0

    # Передача данных в шаблон
    return render(request, 'admin_zone/view_analytics.html', {
        'total_orders': total_orders,
        'total_revenue': round(total_revenue, 2),
        'total_users': total_users,
        'average_order_value': round(average_order_value, 2),
        'users_today': data_today['users'],
        'orders_today': data_today['orders'],
        'revenue_today': data_today['revenue'],
        'average_today': data_today['average_check'],
        'users_week': data_week['users'],
        'orders_week': data_week['orders'],
        'revenue_week': data_week['revenue'],
        'average_week': data_week['average_check'],
        'users_month': data_month['users'],
        'orders_month': data_month['orders'],
        'revenue_month': data_month['revenue'],
        'average_month': data_month['average_check'],
        'users_year': data_year['users'],
        'orders_year': data_year['orders'],
        'revenue_year': data_year['revenue'],
        'average_year': data_year['average_check'],
    })

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TimeSettingsForm
from bot.utils.time_config import load_settings, save_settings  # Импортируем функции загрузки и сохранения настроек

def edit_time_settings(request):
    # Загружаем текущие настройки
    settings = load_settings()

    # Получаем время последнего уведомления (если оно есть)
    last_notified_time = settings.get('last_notified_at', None)
    if last_notified_time:
        last_notified_time = last_notified_time.strftime('%Y-%m-%d %H:%M:%S')  # Форматируем в строку

    if request.method == 'POST':
        form = TimeSettingsForm(request.POST)
        if form.is_valid():
            # Получаем данные из формы
            new_settings = form.cleaned_data

            # Преобразуем данные формы в datetime.time объекты
            new_settings['work_hours_start'] = new_settings['work_hours_start']
            new_settings['work_hours_end'] = new_settings['work_hours_end']

            # Сохраняем новые настройки
            save_settings(new_settings)

            # Обновляем текущие настройки
            settings.update(new_settings)

            messages.success(request, "Настройки времени успешно обновлены.")
            return redirect('admin_zone:edit_time_settings')  # Перенаправляем на текущую страницу после сохранения
    else:
        form = TimeSettingsForm(initial=settings)

    return render(request, 'admin_zone/edit_time_settings.html', {
        'form': form,
        'last_notified_time': last_notified_time  # Передаем время последнего уведомления
    })
