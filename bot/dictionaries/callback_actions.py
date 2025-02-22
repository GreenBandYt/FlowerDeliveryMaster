# callback_actions.py

from bot.handlers.admin import (
    update_user_status_callback,
    analytics_today,
    analytics_week,
    analytics_month,
    analytics_year,
    analytics_all_time,
    analytics_cancel,
    cancel_user_status_callback,
    handle_orders_by_status_new,
    handle_orders_processing,
    handle_orders_completed,
    handle_order_details,
    handle_assign_executor,
    handle_set_executor,
    handle_admin_orders,

)

from bot.handlers.staff import update_order_status


from bot.handlers.common_helpers import feature_in_development

# Словарь callback-действий (инлайн-кнопки)
CALLBACK_ACTIONS = {
    # 🔹 Управление пользователями для Администратора
    "user_status_update": update_user_status_callback,
    "cancel_user_status": cancel_user_status_callback,

    # 🔹 Управление заказами для Администратора
    "order_status_update": update_order_status,
    "orders_new": handle_orders_by_status_new,
    "orders_processing": handle_orders_processing,
    "orders_completed": handle_orders_completed,
    "order_details": handle_order_details,
    "assign_executor": handle_assign_executor,
    "set_executor": handle_set_executor,
    "admin_orders": handle_admin_orders,

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

