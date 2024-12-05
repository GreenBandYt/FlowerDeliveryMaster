from django.shortcuts import render

def catalog_home(request):
    """
    Главная страница каталога.
    """
    return render(request, 'catalog/home.html', {})
