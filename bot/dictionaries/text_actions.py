from bot.handlers.admin.admin_menu import handle_admin_analytics, handle_admin_users, handle_admin_orders, handle_admin_help
from bot.handlers.customer.customer_menu import handle_customer_orders, handle_customer_cart, handle_customer_catalog, handle_customer_help
from bot.handlers.new_user.new_user_menu import handle_new_user_register, handle_new_user_link, handle_new_user_help
from bot.handlers.staff.staff_menu import handle_staff_orders, handle_staff_update_status, handle_staff_help

# Словарь действий для текстовых кнопок (Главное меню)
TEXT_ACTIONS = {
    # 🔹 Администратор
    "📊 Аналитика": handle_admin_analytics,
    "👥 Пользователи": handle_admin_users,
    "📦 Заказы": handle_admin_orders,
    "ℹ️ Помощь": handle_admin_help,

    # 🔹 Клиент (покупатель)
    "📦 Мои заказы": handle_customer_orders,
    "🛒 Корзина": handle_customer_cart,
    "🛍️ Каталог": handle_customer_catalog,
    "ℹ️ Показать помощь": handle_customer_help,

    # 🔹 Новый пользователь
    "🔗 Привязать аккаунт": handle_new_user_link,
    "📝 Зарегистрироваться": handle_new_user_register,
    "🆘 Помощь": handle_new_user_help,

    # 🔹 Сотрудник
    "📦 Текущие заказы": handle_staff_orders,
    "🔄 Обновить статус": handle_staff_update_status,
    "❓  Помощь": handle_staff_help,
}
