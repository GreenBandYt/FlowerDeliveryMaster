import os
import qrcode
from io import BytesIO
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

# Функция для генерации QR-кода, если он еще не создан
def generate_qr_code():
    """
    Генерация и сохранение QR-кода для Telegram-бота, если он еще не создан.
    """
    bot_url = "https://t.me/FlowerDelivery_GBt_Bot"
    qr_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'telegram_bot.png')

    # Проверяем, существует ли файл
    if not os.path.exists(qr_path):
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(bot_url)
        qr.make(fit=True)
        qr.make_image(fill='black', back_color='white').save(qr_path)
        print(f"QR-код сгенерирован и сохранен по пути: {qr_path}")
    else:
        print(f"QR-код уже существует: {qr_path}")


def register(request):
    """
    Представление для регистрации нового пользователя.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)  # Используем кастомную форму
        if form.is_valid():
            user = form.save()  # Сохраняем пользователя и получаем объект

            # Генерация QR-кода
            generate_qr_code()
            qr_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'telegram_bot.png')

            # Создание письма с вложением
            email = EmailMessage(
                subject='Добро пожаловать в Flower Delivery Master!',
                body=(
                    f'Здравствуйте, {user.username}!\n\n'
                    'Спасибо за регистрацию на нашем сайте!\n\n'
                    'Для привязки вашего аккаунта к Telegram-боту, перейдите по следующей ссылке: '
                    f'https://t.me/FlowerDelivery_GBt_Bot и введите команду /link {user.username}.\n\n'
                    'С уважением,\n'
                    'Команда Flower Delivery Master.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )

            # Добавление QR-кода как вложения
            with open(qr_path, 'rb') as qr_file:
                email.attach('telegram_bot.png', qr_file.read(), 'image/png')

            email.send(fail_silently=False)

            # Автоматический вход пользователя
            login(request, user)

            # messages.success(
            #     request,
            #     'Ваш аккаунт успешно создан! Проверьте электронную почту для получения инструкции по привязке Telegram-аккаунта.'
            # )
            return redirect('telegram_info')  # Перенаправляем на страницу с информацией о Telegram-боте
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserCreationForm()  # Инициализация формы для GET-запроса
    return render(request, 'users/register.html', {'form': form})


@login_required
def telegram_info(request):
    """
    Представление для отображения информации о Telegram-боте.
    """
    # Генерация QR-кода, если он еще не создан
    generate_qr_code()

    bot_url = "https://t.me/FlowerDelivery_GBt_Bot"
    qr_path = os.path.join('static', 'images', 'telegram_bot.png')  # Относительный путь для отображения

    # Передача данных в шаблон
    return render(request, 'users/telegram_info.html', {
        'bot_url': bot_url,
        'qr_image_url': qr_path,  # Путь к изображению QR-кода
        'username': request.user.username  # Передаём имя пользователя для персонализации
    })
