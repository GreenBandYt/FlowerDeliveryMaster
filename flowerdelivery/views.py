from django.shortcuts import redirect

def home_redirect(request):
    """
    Главная страница: редирект на login или catalog в зависимости от состояния пользователя.
    """
    if request.user.is_authenticated:
        return redirect('catalog:home')  # Редирект авторизованных пользователей на каталог
    return redirect('login')  # Редирект неавторизованных пользователей на login
