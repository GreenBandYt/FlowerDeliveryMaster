from bot.handlers.admin import update_user_status_callback, update_order_status, analytics_period_handler
from bot.handlers.customer import add_to_cart, remove_from_cart, confirm_checkout, cancel_checkout, decrease_quantity, increase_quantity, delete_item, checkout

# Словарь callback-действий (инлайн-кнопки)
CALLBACK_ACTIONS = {
    # 🔹 Управление пользователями
    "staff_{user_id}_true": update_user_status_callback,   # Назначить пользователя сотрудником
    "staff_{user_id}_false": update_user_status_callback,  # Назначить пользователя клиентом
    "cancel_user_status_{user_id}": update_user_status_callback,  # Отмена изменения статуса пользователя

    # 🔹 Управление заказами
    "status_{order_id}_new": update_order_status,        # Статус заказа: Новый
    "status_{order_id}_processing": update_order_status, # Статус заказа: В процессе
    "status_{order_id}_completed": update_order_status,  # Статус заказа: Завершен
    "cancel_order_status_{order_id}": update_order_status,  # Отмена изменения статуса заказа

    # 🔹 Аналитика
    "analytics_today": analytics_period_handler,   # Аналитика за сегодня
    "analytics_week": analytics_period_handler,    # Аналитика за неделю
    "analytics_month": analytics_period_handler,   # Аналитика за месяц
    "analytics_year": analytics_period_handler,    # Аналитика за год
    "analytics_all": analytics_period_handler,     # Аналитика за всё время
    "analytics_cancel": analytics_period_handler,  # Отмена аналитики

    # 🔹 Клиент (покупатель)
    "add_to_cart_{product_id}": add_to_cart,  # Добавить в корзину
    "remove_from_cart_{product_id}": remove_from_cart,  # Удалить из корзины
    "confirm_checkout": confirm_checkout,  # Подтвердить оформление
    "cancel_checkout": cancel_checkout,  # Отменить оформление
    "decrease_{product_id}": decrease_quantity,  # Уменьшить количество
    "increase_{product_id}": increase_quantity,  # Увеличить количество
    "delete_{product_id}": delete_item,  # Удалить товар
    "checkout": checkout,  # Оформить заказ
}
