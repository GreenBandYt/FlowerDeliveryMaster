# bot/utils/time_utils.py

import datetime
import pytz
from bot.utils.time_config import WORK_HOURS_START, WORK_HOURS_END

MOSCOW_TZ = pytz.timezone("Europe/Moscow")

def is_working_hours():
    """
    Проверяет, находится ли текущее время в пределах рабочего графика.
    Возвращает True, если сейчас рабочее время, иначе False.
    """
    now = datetime.datetime.now(MOSCOW_TZ).time()
    return WORK_HOURS_START <= now <= WORK_HOURS_END
