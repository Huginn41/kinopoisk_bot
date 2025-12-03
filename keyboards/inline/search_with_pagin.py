from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def inline_search_keyboard(current_index: int, total_results: int) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру с пагинацией для результатов поиска.

    :param current_index: Текущий индекс фильма
    :type current_index: int
    :param total_results: Общее количество результатов
    :type total_results: int
    :return: Объект клавиатуры
    :rtype: InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=3)

    current_page = current_index + 1
    total_pages = total_results

    page_button = InlineKeyboardButton(
        text=f"{current_page}/{total_pages}",
        callback_data="disabled"
    )

    if current_index == 0:
        prev_button = InlineKeyboardButton("⚫️", callback_data="disabled")
    else:
        prev_button = InlineKeyboardButton("⬅️", callback_data=f"prev_{current_index - 1}")

    if current_index >= total_results - 1:
        next_button = InlineKeyboardButton("⚫", callback_data="disabled")
    else:
        next_button = InlineKeyboardButton("➡️", callback_data=f"next_{current_index + 1}")

    keyboard.add(prev_button, page_button, next_button)

    keyboard.add(
        InlineKeyboardButton("📌 Смотреть позже", callback_data=f"watch_later_{current_index}"),
        InlineKeyboardButton("🏠 В главное меню", callback_data="main_menu")
    )

    return keyboard
