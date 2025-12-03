from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def inline_history_keyboard(current_index: int, total_results: int, is_watched: bool = False) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для элементов истории.

    :param current_index: Текущий индекс
    :type current_index: int
    :param total_results: Общее количество элементов
    :type total_results: int
    :param is_watched: Отмечен ли как просмотренный
    :type is_watched: bool
    :return: Объект клавиатуры
    :rtype: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=3)

    page_btn = InlineKeyboardButton(f"{current_index + 1}/{total_results}", callback_data="history_disabled")

    if current_index == 0:
        prev_btn = InlineKeyboardButton("⚫️", callback_data="history_disabled")
    else:
        prev_btn = InlineKeyboardButton("⬅️", callback_data=f"history_prev_{current_index - 1}")

    if current_index >= total_results - 1:
        next_btn = InlineKeyboardButton("⚫", callback_data="history_disabled")
    else:
        next_btn = InlineKeyboardButton("➡️", callback_data=f"history_next_{current_index + 1}")

    keyboard.add(prev_btn, page_btn, next_btn)

    if is_watched:
        watch_btn = InlineKeyboardButton("Просмотрено", callback_data="history_disabled")
    else:
        watch_btn = InlineKeyboardButton("Отметить просмотренным", callback_data=f"history_mark_watched_{current_index}")

    keyboard.add(watch_btn)
    keyboard.add(InlineKeyboardButton("Главное меню", callback_data="history_main_menu"))

    return keyboard
