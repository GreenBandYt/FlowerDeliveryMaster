from django import forms

class OrderForm(forms.Form):
    """
    Форма для оформления заказа.
    Позволяет пользователю указать адрес доставки и комментарии.
    """
    address = forms.CharField(
        label='Адрес доставки',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите адрес доставки',
        }),
    )
    comments = forms.CharField(
        label='Комментарии к заказу',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Дополнительная информация (не обязательно)',
            'rows': 3,
        }),
    )

class ReviewForm(forms.Form):
    """
    Форма для добавления отзыва.
    Позволяет пользователю указать рейтинг и текст отзыва.
    """
    rating = forms.ChoiceField(
        label='Рейтинг',
        choices=[(i, f"{i} звёзд") for i in range(1, 6)],
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
    )
    review_text = forms.CharField(
        label='Текст отзыва',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Напишите ваш отзыв здесь...',
            'rows': 3,
        }),
    )
