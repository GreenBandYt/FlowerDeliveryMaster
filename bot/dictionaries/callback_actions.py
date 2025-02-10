# callback_actions.py

from bot.handlers.admin import (
    update_user_status_callback, update_order_status, analytics_period_handler, handle_cancel_manage_users
)
from bot.handlers.common_helpers import feature_in_development

# Словарь callback-действий (инлайн-кнопки)
CALLBACK_ACTIONS = {
    # 🔹 Управление пользователями для Администратора
    "user_status_update": update_user_status_callback,  # Изменение статуса пользователя
    "cancel_user_management": handle_cancel_manage_users,  # Отмена управления пользователями

    # 🔹 Управление заказами для Администратора
    "order_status_update": update_order_status,  # Изменение статуса заказа

    # 🔹 Аналитика для Администратора
    "analytics_period": analytics_period_handler,  # Выбор периода аналитики

    # 🔧 В разработке
    "feature_in_development": feature_in_development,
}
