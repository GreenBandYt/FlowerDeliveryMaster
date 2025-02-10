# bot/utils/callback_parser.py

def parse_callback_data(callback_data: str):
    """
    Унифицированный парсер callback_data.
    Формат данных: action:param1:param2
    """
    parts = callback_data.split(":")
    if len(parts) < 2:
        return None, None
    action = parts[0]
    params = parts[1:]
    return action, params

