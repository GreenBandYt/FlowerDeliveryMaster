from django.db import models
from django.conf import settings


# Модель продукта
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Product Name")  # Название продукта
    description = models.TextField(blank=True, verbose_name="Description")  # Описание продукта
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")  # Цена продукта
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Image")  # Изображение продукта
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")  # Дата создания записи
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")  # Дата последнего обновления записи

    def __str__(self):
        return self.name  # Возвращает строковое представление продукта


# Модель корзины
class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="User"
    )  # Связь корзины с пользователем (может быть пустой, если пользователь анонимный)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")  # Дата создания корзины
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")  # Дата последнего обновления корзины

    def get_total_price(self):
        """
        Рассчитывает общую стоимость всех товаров в корзине.
        """
        return sum(item.price for item in self.items.all())

    def __str__(self):
        return f"Cart {self.id} for {self.user if self.user else 'Anonymous'}"  # Возвращает строковое представление корзины


# Модель элемента корзины
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name="Cart"
    )  # Связь элемента корзины с корзиной
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Product"
    )  # Связь элемента корзины с продуктом
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")  # Количество продукта
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Price"
    )  # Итоговая стоимость элемента корзины

    def save(self, *args, **kwargs):
        """
        Переопределяет метод сохранения для автоматического расчета итоговой стоимости.
        """
        self.price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"  # Строковое представление элемента корзины


# Модель заказа
class Order(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),  # Заказ создан
        ('processed', 'Processed'),  # Заказ в обработке
        ('shipped', 'Shipped'),  # Заказ отправлен
        ('delivered', 'Delivered'),  # Заказ доставлен
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="User"
    )  # Связь заказа с пользователем
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")  # Дата создания заказа
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='created',
        verbose_name="Order Status"
    )  # Статус заказа
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Price")  # Общая стоимость заказа
    notes = models.TextField(blank=True, null=True, verbose_name="Order Notes")  # Заметки к заказу

    def __str__(self):
        return f"Order {self.id} by {self.user}"  # Строковое представление заказа


# Модель элемента заказа
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name="Order"
    )  # Связь элемента заказа с заказом
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Product"
    )  # Связь элемента заказа с продуктом
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")  # Количество продукта
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total Price"
    )  # Итоговая стоимость элемента заказа

    def save(self, *args, **kwargs):
        """
        Переопределяет метод сохранения для автоматического расчета итоговой стоимости.
        """
        self.price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"  # Строковое представление элемента заказа
