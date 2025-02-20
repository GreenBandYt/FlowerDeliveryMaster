# callback_actions.py

from bot.handlers.admin import (
    update_user_status_callback,
    analytics_today,
    analytics_week,
    analytics_month,
    analytics_year,
    analytics_all_time,
    analytics_cancel,
)

from bot.handlers.staff import update_order_status


from bot.handlers.common_helpers import feature_in_development

# Словарь callback-действий (инлайн-кнопки)
CALLBACK_ACTIONS = {
    # 🔹 Управление пользователями для Администратора
    "user_status_update": update_user_status_callback,
    # "cancel_user_management": "handle_cancel_manage_users",

    # 🔹 Управление заказами для Администратора
    "order_status_update": update_order_status,

    # 🔹 Аналитика для Администратора (НОВЫЙ ПОДХОД)
    "analytics_today": analytics_today,
    "analytics_week": analytics_week,
    "analytics_month": analytics_month,
    "analytics_year": analytics_year,
    "analytics_all_time": analytics_all_time,
    "analytics_cancel": analytics_cancel,

    # 🔧 В разработке
    "feature_in_development": feature_in_development,
}

