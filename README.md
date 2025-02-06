# **Привет! Меня зовут Юрий** / <img src="https://raw.githubusercontent.com/GreenBandYt/GreenBandYt/main/assets/images/b_logo_g.png" width="25" alt="G" style="vertical-align: -2px;">reenBandYt

<p>
  <a href="https://github.com/GreenBandYt" target="_blank" rel="noopener noreferrer">
    <img src="https://img.shields.io/badge/GreenBandYt-Зелёный_код_жизни-32CD32?style=for-the-badge&logo=leaflet&logoColor=white">
  </a>
  &nbsp;&nbsp;
  <img src="https://raw.githubusercontent.com/GreenBandYt/GreenBandYt/main/assets/logos/zerocoder.png" width="28" height="28" alt="Zerocoder" style="vertical-align: middle; border-radius: 50%;">
  <a href="https://github.com/GreenBandYt/Zerocoder/blob/main/README.md" target="_blank" rel="noopener noreferrer">
    <img src="https://img.shields.io/badge/Zerocoder-Выпускник-%239B59B6?style=for-the-badge">
  </a>
</p>

**Python-разработчик | Telegram-боты | Веб-приложения | Базы данных**  
**"Зелёный код жизни" – код, который растёт вместе с тобой!**

---

### **FlowerDeliveryMaster🚀**
**Итоговый проект по курсу "Программист на Python с нуля с помощью ChatGPT. [python-ai] 7 поток"**  

FlowerDeliveryMaster — это веб-приложение для онлайн-доставки цветов с возможностью интеграции Telegram-бота. Проект включает в себя функции управления заказами, корзиной, отзывами и администраторскую панель.

---

## 📋 **Функциональность проекта**

1. **Управление товарами**  
   - Просмотр каталога товаров (цветов).  
   - Детальная страница товара с отзывами и рейтингами.  

2. **Корзина**  
   - Добавление/удаление товаров.  
   - Обновление количества позиций.  
   - Оформление заказа.  

3. **Управление заказами**  
   - Просмотр истории заказов.  
   - Повторение заказов.  
   - Удаление заказов.  

4. **Отзывы и рейтинги**  
   - Оставление отзывов на товары.  
   - Пагинация для просмотра всех отзывов.  

5. **Админ-зона**  
   - Доступ для администраторов для управления заказами и аналитикой.  

---

## 💻 **Технологии**

- **Backend**: Python 3.12, Django 5.1.3  
- **Frontend**: HTML, CSS, Bootstrap  
- **Database**: SQLite  
- **Дополнительно**: Django Forms, Messages, Paginator  
- **Тестирование**: pytest, pytest-django  

---

## 🚀 **Установка и запуск проекта**

### **1. Клонирование репозитория**
```bash
git clone https://github.com/GreenBandYt/FlowerDeliveryMaster.git
cd FlowerDeliveryMaster
```

### **2. Создание виртуального окружения**
```bash
python -m venv .venv
source .venv/bin/activate      # Для Linux/Mac
.venv\Scripts\activate         # Для Windows
```

### **3. Установка зависимостей**
```bash
pip install -r requirements.txt
```

### **4. Применение миграций**
```bash
python manage.py makemigrations
python manage.py migrate
```

### **5. Создание суперпользователя**
```bash
python manage.py createsuperuser
```

### **6. Запуск сервера**
```bash
python manage.py runserver
```

После запуска, проект будет доступен по адресу:  
📍 **[https://bandurayvgpt.pythonanywhere.com](https://bandurayvgpt.pythonanywhere.com)**  

---

## ✅ **Запуск тестов**

Для запуска тестов используй команду:
```bash
pytest tests/
```

---

## 📂 **Структура проекта**

```
FlowerDeliveryMaster/
│
├── catalog/                 # Основное приложение (товары, заказы, отзывы)
│   ├── models.py            # Модели данных (Product, Cart, Order, Review)
│   ├── views.py             # Представления
│   ├── urls.py              # URL-маршруты
│   ├── forms.py             # Формы для отзывов и заказов
│   └── templates/           # Шаблоны для отображения
│
├── users/                   # Кастомная модель пользователя
│
├── tests/                   # Тесты
│   ├── test_models.py       # Тесты моделей
│   ├── test_views.py        # Тесты представлений
│   ├── test_forms.py        # Тесты форм
│   └── test_urls.py         # Тесты маршрутов
│
├── flowerdelivery/          # Настройки Django
│   ├── settings.py          # Конфигурация проекта
│   └── urls.py              # Основные маршруты
│
├── static/                  # Статические файлы (CSS, JS)
├── media/                   # Медиафайлы пользователей
└── requirements.txt         # Список зависимостей
```

---

## 🛠 **Доработки и идеи**

- Интеграция Telegram-бота для уведомлений о статусе заказов.  
- Добавление аналитики и отчетов для администраторов.  
- Улучшение стилей с помощью Bootstrap и JavaScript.  

---

## ✨ **Автор**

<a href="https://github.com/GreenBandYt" target="_blank" rel="noopener noreferrer">
Разработано в рамках учебного проекта.  

### 📬 Контакты

- **Email:** [bandurayv@yandex.ru](mailto:bandurayv@yandex.ru)
- **Telegram:** [@BandYuraV](https://t.me/BandYuraV)


---

## 🔖 **Лицензия**

Этот проект распространяется под лицензией **MIT**.
```
