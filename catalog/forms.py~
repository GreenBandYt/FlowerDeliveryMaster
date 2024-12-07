from django import forms

class OrderForm(forms.Form):
    """
    Форма для оформления заказа.
    Позволяет пользователям вводить данные для доставки и оставлять комментарии к заказу.
    """
    name = forms.CharField(
        label='Имя',  # Надпись рядом с полем
        max_length=100,  # Ограничение длины текста
        widget=forms.TextInput(attrs={  # HTML-атрибуты для стиля и подсказок
            'class': 'form-control',  # Bootstrap-класс для оформления
            'placeholder': 'Введите ваше имя',  # Подсказка внутри поля
        }),
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш телефон',
        }),
    )
    address = forms.CharField(
        label='Адрес доставки',
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите адрес доставки',
        }),
    )
    comments = forms.CharField(
        label='Комментарии к заказу',  # Комментарии для дополнительной информации
        required=False,  # Поле не обязательно для заполнения
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Дополнительная информация',  # Подсказка для пользователя
            'rows': 3,  # Высота текстового поля
        }),
    )
