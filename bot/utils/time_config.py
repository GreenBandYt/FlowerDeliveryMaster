import datetime
import json

# 🔹 Рабочее время (часы и минуты)
WORK_HOURS_START = datetime.time(9, 0)  # 09:00
WORK_HOURS_END = datetime.time(22, 0)  # 20:00

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

SETTINGS_FILE = 'time_settings.json'


def load_settings():
    """
    Загружает настройки времени из файла.
    """
    try:
        with open(SETTINGS_FILE, 'r') as file:
            settings = json.load(file)

            # Преобразуем строковые значения времени обратно в datetime.time
            settings['work_hours_start'] = datetime.datetime.strptime(settings['work_hours_start'], '%H:%M').time()
            settings['work_hours_end'] = datetime.datetime.strptime(settings['work_hours_end'], '%H:%M').time()

            return settings
    except FileNotFoundError:
        return {
            'work_hours_start': datetime.time(9, 0),  # Начало рабочего времени
            'work_hours_end': datetime.time(20, 0),  # Конец рабочего времени
            'new_order_notify_interval': 1,  # Интервал для уведомлений о новых заказах
            'repeat_order_notify_interval': 2,  # Интервал для повторных уведомлений
            'allow_non_working_hours_notifications': False,  # Разрешение уведомлений вне рабочего времени
        }


def save_settings(settings):
    """
    Сохраняет обновленные настройки времени в файл.
    """
    settings['work_hours_start'] = settings['work_hours_start'].strftime('%H:%M')
    settings['work_hours_end'] = settings['work_hours_end'].strftime('%H:%M')

    with open(SETTINGS_FILE, 'w') as file:
        json.dump(settings, file, indent=4)

