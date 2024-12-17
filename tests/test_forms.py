import pytest
from catalog.forms import OrderForm, ReviewForm

def test_order_form_valid_data():
    form = OrderForm(data={
        'address': 'Test Address 123',
        'comments': 'Test order comments'
    })
    assert form.is_valid()

def test_order_form_invalid_data():
    form = OrderForm(data={})
    assert not form.is_valid()
    assert 'address' in form.errors

def test_review_form_valid_data():
    form = ReviewForm(data={
        'rating': 5,
        'review_text': 'Great product!'
    })
    assert form.is_valid()

def test_review_form_invalid_data():
    form = ReviewForm(data={
        'rating': '',
        'review_text': ''
    })
    assert not form.is_valid()
    assert 'rating' in form.errors
