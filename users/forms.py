from django import forms
from users.models import CustomUser

class CustomUserCreationForm(forms.ModelForm):
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
        fields = ('username', 'email')
        labels = {
            'username': 'Имя пользователя',
            'email': 'Адрес электронной почты',
        }
        help_texts = {
            'username': 'Обязательное поле. Не более 150 символов. Только буквы, цифры и символы @/./+/-/_',
            'email': 'Введите действующий адрес электронной почты.',
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
