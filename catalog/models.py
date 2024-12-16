from django.db import models
from django.conf import settings
from django.db.models import Avg
import asyncio
import importlib
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

# Модель продукта
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Product Name")
    description = models.TextField(blank=True, verbose_name="Description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Image")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def get_average_rating(self):
        average = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(average, 1) if average else 'Нет рейтинга'

    def __str__(self):
        return self.name


# Модель корзины
class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="User"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def get_total_price(self):
        return sum(item.price for item in self.items.all())

    def __str__(self):
        return f"Cart {self.id} for {self.user if self.user else 'Anonymous'}"


# Модель элемента корзины
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name="Cart"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Product"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Price")

    def save(self, *args, **kwargs):
        self.price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"


# Модель заказа
class Order(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('processed', 'Processed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="User"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='created',
        verbose_name="Order Status"
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Price")
    notes = models.TextField(blank=True, null=True, verbose_name="Order Notes")
    address = models.TextField(blank=True, null=True, verbose_name="Address")

    def __str__(self):
        return f"Order {self.id} by {self.user}"


# Модель элемента заказа
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name="Order"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Product"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Price")

    def save(self, *args, **kwargs):
        self.price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"


# Модель отзывов
class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="User"
    )
    product = models.ForeignKey(
        Product,
        related_name="reviews",
        on_delete=models.CASCADE,
        verbose_name="Product"
    )
    rating = models.PositiveIntegerField(
        verbose_name="Rating",
        default=1,
        choices=[(i, i) for i in range(1, 6)]
    )
    review_text = models.TextField(blank=True, null=True, verbose_name="Review Text")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"Review by {self.user} on {self.product.name}"


@receiver(post_save, sender=Order)
def notify_new_order(sender, instance, created, **kwargs):
    """
    Сигнал для отправки уведомления о новом заказе всем сотрудникам.
    """
    if created:
        logger.info(f"Сигнал сработал: создан заказ #{instance.id}")
        try:
            # Динамический импорт функции
            bot_logic = importlib.import_module('bot.bot_logic')
            send_new_order_notification = getattr(bot_logic, 'send_new_order_notification')

            # Вызов функции напрямую
            send_new_order_notification(instance)

        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления о заказе: {e}", exc_info=True)
