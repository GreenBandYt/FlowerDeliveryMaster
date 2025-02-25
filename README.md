<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/Flower_Delivery_Logo.png" width="150">
</p>

# 🌸 **Flower Delivery Master**  
🚀 **Полноценная система для управления цветочным бизнесом** – включает **веб-приложение (Django) + Telegram-бот**.  

---

## 📌 **1. О проекте**  
✅ Веб-приложение предоставляет удобный **каталог**, **корзину**, **оформление заказов**, а также **админ-зону** для управления заказами и аналитики.  
✅ Telegram-бот позволяет клиентам **делать заказы**, сотрудникам **взять заказ в работу**, а администраторам **управлять пользователями и аналитикой**.  
✅ **Контроль рабочего времени** – заказы можно оформлять только в рабочие часы.  

---

## 🌍 **2. Веб-приложение (Django)**  
### ✨ **Основные функции**  
✔ **Регистрация и авторизация** (система пользователей Django).  
✔ **Каталог** цветов, **корзина**, **оформление заказа**.  
✔ **История заказов, повторный заказ**.  
✔ **Админ-зона**: управление заказами, статусами, пользователями.  
✔ **E-mail уведомления** клиентам и сотрудникам.  
✔ **Работа со статическими (`static/`) и медиа (`media/`) файлами**.  

### 🛠 **Технологии**  
🔹 **Django 5.1.3** – основа веб-приложения.  
🔹 **SQLite** – для хранения заказов, товаров и пользователей.  
🔹 **Django ORM** – работа с базой данных.  
🔹 **dotenv** – загрузка конфигурации из `.env`.  

---

## 🤖 **3. Telegram-бот**  
Бот интегрирован с Django и управляет всеми процессами **через один Telegram-интерфейс**.  

### 🚀 **Уникальные особенности**  
✔ **Централизованная обработка команд и кнопок**.  
✔ **Уведомления** о новых заказах, статусах и назначениях.  
✔ **Контроль рабочего времени** – заказы принимаются **с 09:00 до 18:00**.  
✔ **Гибкое управление ролями** – **админы, сотрудники, клиенты, новые пользователи**.  

### 🧠 **Как бот обрабатывает команды и кнопки?**  
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

## 👥 **4. Разграничение ролей в системе**  
| **Роль**            | **Функции** |
|---------------------|------------|
| **Администратор**  | Управление заказами, пользователями, аналитика. |
| **Сотрудник**      | Взятие заказов в работу, завершение, отмена. |
| **Клиент**         | Каталог, корзина, оформление и повтор заказов. |
| **Незарегистрированный** | Привязка аккаунта, регистрация. |

---

## 📢 **5. Система уведомлений и контроль рабочего времени**  
✔ **Бот уведомляет администраторов и сотрудников о новых заказах**.  
✔ **Напоминает о заказах, если их долго не берут в работу**.  
✔ **Контролирует рабочее время** – заказы оформляются **только с 09:00 до 18:00**.  
✔ **В нерабочее время кнопка оформления заказа блокируется**.  

## 🛠 **6. Установка и запуск проекта**  
### **1. Установка зависимостей**  
```bash
pip install -r requirements.txt
```
### **2. Настройка `.env`**  
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

## ✅ **7. Запуск тестов**  
Для запуска тестов используй команду:
```bash
pytest tests/
```

---

## 💡 **8. Доработки и идеи**
- 🔥 **Интеграция уведомлений** в Telegram-бота о статусе заказов.  
- 📊 **Аналитика и отчёты** для администраторов.  
- 🎨 **Улучшение UI** с Bootstrap и JavaScript.  

---

## 🔖 **9. Лицензия**
Этот проект распространяется под лицензией **MIT**.

---

## ✨ **10. Автор** Юрий Бандура
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
