from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def genre_keyboard() -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру с жанрами.

    :return: Объект клавиатуры
    :rtype: InlineKeyboardMarkup
    """
    genres = [
        "драма", "комедия", "боевик",
        "фантастика", "триллер", "мелодрама",
        "ужасы", "детектив", "приключения"
    ]

    keyboard = InlineKeyboardMarkup(row_width=2)

    for genre in genres:
        keyboard.add(InlineKeyboardButton(genre.title(), callback_data=f"genre_{genre}"))

    keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel_rating_search"))

    return keyboard
