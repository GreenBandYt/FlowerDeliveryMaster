import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model  # Используем кастомную модель
from catalog.models import Cart
from django.test import Client

User = get_user_model()  # Получаем текущую модель пользователя

@pytest.mark.django_db
def test_cart_view():
    user = User.objects.create_user(username="testuser", password="password123")
    client = Client()
    client.login(username="testuser", password="password123")

    cart = Cart.objects.create(user=user)
    response = client.get(reverse('catalog:cart'))
    assert response.status_code == 200
    assert 'catalog/cart.html' in [t.name for t in response.templates]

@pytest.mark.django_db
def test_checkout_view_empty_cart():
    user = User.objects.create_user(username="testuser", password="password123")
    client = Client()
    client.login(username="testuser", password="password123")

    response = client.get(reverse('catalog:checkout'))
    assert response.status_code == 302  # Перенаправление, если корзина пуста
