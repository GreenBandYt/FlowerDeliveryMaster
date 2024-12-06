from django.db import models  # Добавлен импорт
from .models import Cart

def cart_count(request):
    """
    Контекстный процессор для отображения количества товаров в корзине.
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        count = cart.items.aggregate(total_quantity=models.Sum('quantity'))['total_quantity'] or 0
        return {'cart_count': count}
    return {'cart_count': 0}
