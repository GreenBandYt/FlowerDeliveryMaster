import pytest
from catalog.models import Order
from django.contrib.auth import get_user_model

@pytest.mark.django_db
def test_order_creation():
    User = get_user_model()
    user = User.objects.create_user(username="testuser", password="password123")

    order = Order.objects.create(
        user=user,
        total_price=250.50,
        address="Test Address, 123",
        notes="Test order note",
        status="created",
        is_ready=False
    )

    assert order.user.username == "testuser"
    assert order.total_price == 250.50
    assert order.address == "Test Address, 123"
    assert order.notes == "Test order note"
    assert order.status == "created"
    assert order.is_ready is False
