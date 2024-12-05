from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    """
    Представление для регистрации нового пользователя.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Используем кастомную форму
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created! You can now log in.')
            return redirect('login')  # После успешной регистрации перенаправляем на login
    else:
        form = CustomUserCreationForm()  # Инициализация формы для GET-запроса
    return render(request, 'users/register.html', {'form': form})
