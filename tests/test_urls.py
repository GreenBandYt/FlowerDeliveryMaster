from django.urls import reverse, resolve
from catalog.views import order_history  # Используем существующую функцию

def test_order_history_url():
    path = reverse('catalog:order_history')  # Проверь, что имя маршрута существует
    resolved_func = resolve(path).func
    assert resolved_func == order_history
