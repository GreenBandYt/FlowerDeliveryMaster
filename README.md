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

Спасибо! 🔥 Теперь готов собрать **итоговый README** для всего проекта!  

Вот **структура**, которую я предлагаю:  

---
# **README для Flower Delivery Master**  

## 1️⃣ О проекте  
📌 **Краткое описание** (веб-приложение + бот).  
📌 **Основные функции** (каталог, корзина, заказы, уведомления).  

## 2️⃣ Веб-приложение (Django)  
✔ Регистрация и авторизация.  
✔ Каталог, корзина, заказы.  
✔ Админ-зона: управление заказами, аналитика.  
✔ E-mail уведомления.  
✔ Контроль рабочего времени.  

## 3️⃣ Telegram-бот  
✔ Уникальная **универсальная обработка команд** и кнопок.  
✔ Роли пользователей: **админы, сотрудники, клиенты, новые пользователи**.  
✔ Уведомления и контроль времени.  

## 4️⃣ Установка и запуск  
📌 **Запуск Django-приложения**.  
📌 **Запуск бота** (автозапуск вместе с Django).  

## 5️⃣ Технические особенности  
📌 **Python, Django, TeleBot**.  
📌 **Асинхронная обработка**.  
📌 **Интеграция бота и веб-приложения**.  

---

### **🔥 Начинаю писать финальный README!** 🚀  
Если что-то поменяется по структуре – говори!

📌 **Готов финальный README для всего проекта** 🎉  
Проверяй, и если что-то надо доработать – говори! 🚀  

---

# **Flower Delivery Master** 🌸  
**Полноценная система для управления цветочным бизнесом** – включает **веб-приложение (Django) + Telegram-бот**.  

## **1️⃣ О проекте**  
📌 Веб-приложение предоставляет удобный **каталог**, **корзину**, **оформление заказов**, а также **админ-зону** для управления заказами и аналитики.  
📌 Telegram-бот позволяет клиентам **делать заказы**, сотрудникам **взять заказ в работу**, а администраторам **управлять пользователями и аналитикой**.  
📌 **Контроль рабочего времени** – заказы можно оформлять только в рабочие часы.  

---

## **2️⃣ Веб-приложение (Django)**  
### **Основные функции**  
✔ **Регистрация и авторизация** (система пользователей Django).  
✔ **Каталог** цветов, **корзина**, **оформление заказа**.  
✔ **История заказов, повторный заказ**.  
✔ **Админ-зона**: управление заказами, статусами, пользователями.  
✔ **E-mail уведомления** клиентам и сотрудникам.  
✔ **Работа со статическими (`static/`) и медиа (`media/`) файлами**.  

### **Технологии**  
🛠 **Django 5.1.3** – основа веб-приложения.  
🛠 **SQLite** – для хранения заказов, товаров и пользователей.  
🛠 **Django ORM** – работа с базой данных.  
🛠 **dotenv** – загрузка конфигурации из `.env`.  

---

## **3️⃣ Telegram-бот** 🤖  
Бот интегрирован с Django и управляет всеми процессами **через один Telegram-интерфейс**.  

### **Уникальные особенности**  
✔ **Централизованная обработка команд и кнопок** 🚀  
✔ **Уведомления** о новых заказах, статусах и назначениях.  
✔ **Контроль рабочего времени** – заказы принимаются **с 09:00 до 18:00**.  
✔ **Гибкое управление ролями** – **админы, сотрудники, клиенты, новые пользователи**.  

### **Как бот обрабатывает команды и кнопки?**  
**📩 Универсальный обработчик текста** (`handlers/common.py`):  
1️⃣ Проверяет **состояние пользователя** (`state`).  
2️⃣ Определяет **роль пользователя** (админ, сотрудник, клиент).  
3️⃣ Проверяет команду в **словаре `TEXT_ACTIONS`** и вызывает нужный обработчик.  
4️⃣ Если команда не найдена – ищет **умный ответ (`smart_replies`)**.  
5️⃣ Если нет совпадений – отправляет стандартное сообщение.  

**🔄 Универсальный обработчик callback-кнопок** (`handle_inline_buttons`):  
1️⃣ Проверяет callback **в словаре `CALLBACK_ACTIONS`**.  
2️⃣ Если нет точного совпадения – ищет **динамический обработчик** (например, `staff_take_order:123`).  
3️⃣ Вызывает соответствующую функцию.  

🔹 **Это делает систему гибкой, масштабируемой и удобной для поддержки!**  

---

## **4️⃣ Разграничение ролей в системе**  
| **Роль**            | **Функции** |
|---------------------|------------|
| **Администратор**  | Управление заказами, пользователями, аналитика. |
| **Сотрудник**      | Взятие заказов в работу, завершение, отмена. |
| **Клиент**         | Каталог, корзина, оформление и повтор заказов. |
| **Незарегистрированный** | Привязка аккаунта, регистрация. |

---

## **5️⃣ Система уведомлений и контроль рабочего времени**  
✔ **Бот уведомляет администраторов и сотрудников о новых заказах**.  
✔ **Напоминает о заказах, если их долго не берут в работу**.  
✔ **Контролирует рабочее время** – заказы оформляются **только с 09:00 до 18:00**.  
✔ **В нерабочее время кнопка оформления заказа блокируется**.  

---

## **6️⃣ Установка и запуск проекта**  
### **1. Установка зависимостей**  
```bash
pip install -r requirements.txt
```
### **2. Настройка .env**  
Создайте `.env` и добавьте:  
```
DJANGO_SECRET_KEY=ваш_секретный_ключ
TELEGRAM_BOT_TOKEN=токен_бота
EMAIL_HOST_USER=ваш_email@yandex.ru
EMAIL_HOST_PASSWORD=пароль_от_email
```

### **3. Запуск веб-приложения (Django)**  
```bash
python manage.py migrate  # Применить миграции
python manage.py createsuperuser  # Создать администратора
python manage.py runserver  # Запуск Django-сервера
```

### **4. Запуск Telegram-бота**  
📌 Автозапуск вместе с Django-сервером:  
```bash
python manage.py runserver
```
📌 Запуск отдельно (в продакшене):  
```bash
python bot/bot_runner.py
```

---

## **7️⃣ Технические особенности**  
✔ **Python 3 + Django 5.1.3 + `python-telegram-bot` 20.3**.  
✔ **Асинхронная обработка (`async/await`)**.  
✔ **Интеграция бота с Django ORM**.  
✔ **Использование `InlineKeyboardMarkup` для кнопок в боте**.  
✔ **Чёткое разграничение ролей и управление заказами**.  

---

🔥 **Теперь README полностью готов!** 💪  
🚀 **Проверяй, всё ли правильно, и если надо что-то добавить – говори!** 😃

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
    <img src="https://img.shields.io/badge/GreenBandYt-Зелёный_код_жизни-32CD32?style=for-the-badge&logo=leaflet&logoColor=white">
  </a>
  
- Разработано в рамках учебного проекта.

---

### 📬 Контакты

- **Email:** [bandurayv@yandex.ru](mailto:bandurayv@yandex.ru)
- **Telegram:** [@BandYuraV](https://t.me/BandYuraV)
- **GinHub:** [GreenBandYt](https://github.com/GreenBandYt)

---

## 🔖 **Лицензия**

Этот проект распространяется под лицензией **MIT**.
```
