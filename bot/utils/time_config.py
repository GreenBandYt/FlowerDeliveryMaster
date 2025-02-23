# bot/utils/time_config.py

import datetime

# 🔹 Рабочее время (часы и минуты)
WORK_HOURS_START = datetime.time(9, 0)   # 09:00
WORK_HOURS_END = datetime.time(20, 0)    # 21:00

# 🔹 Интервал проверки новых заказов (минуты)
NEW_ORDER_NOTIFY_INTERVAL = 1

# 🔹 Интервал повторного уведомления, если заказ не взят (минуты)
REPEAT_ORDER_NOTIFY_INTERVAL = 2

# 🔹 Минимальный интервал между уведомлениями одному и тому же сотруднику (минуты)
MIN_NOTIFICATION_INTERVAL = 15

# 🔹 Разрешать ли уведомления вне рабочего времени (по умолчанию False)
ALLOW_NON_WORKING_HOURS_NOTIFICATIONS = False

# 🔹 Время последнего уведомления (будет обновляться в коде)
LAST_NOTIFIED_AT = None  # Формат: "YYYY-MM-DD HH:MM:SS"
