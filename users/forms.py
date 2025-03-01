from django import forms
from users.models import CustomUser
import re

class CustomUserCreationForm(forms.ModelForm):
    phone_number = forms.CharField(
        label='Номер телефона',
        max_length=16,
        help_text='Введите номер телефона в формате +7(XXX)XXX-XX-XX.',
        widget=forms.TextInput(attrs={
            'pattern': r'\+7\(\d{3}\)\d{3}-\d{2}-\d{2}',  # HTML5-проверка формата
            'title': 'Номер телефона должен быть в формате +7(XXX)XXX-XX-XX.',
        }),
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        help_text='Придумайте надёжный пароль.',
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput,
        help_text='Введите тот же пароль, что и выше, для проверки.',
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone_number')
        labels = {
            'username': 'Имя пользователя',
            'email': 'Адрес электронной почты',
            'phone_number': 'Номер телефона',
        }
        help_texts = {
            'username': 'Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_',
            'email': 'Введите действующий адрес электронной почты.',
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        pattern = r'^\+7\(\d{3}\)\d{3}-\d{2}-\d{2}$'
        if not re.fullmatch(pattern, phone_number):
            raise forms.ValidationError(
                'Номер телефона должен быть в формате +7(XXX)XXX-XX-XX.'
            )
        return phone_number

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.phone_number = self.cleaned_data.get('phone_number')  # Явное сохранение номера телефона
        if commit:
            user.save()
        return user
