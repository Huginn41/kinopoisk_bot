from telebot import types


def genre_keyboard() -> types.ReplyKeyboardMarkup:
    """
    Создает реплай-клавиатуру с жанрами.

    :return: Объект клавиатуры
    :rtype: types.ReplyKeyboardMarkup
    """
    genres = [
        "драма", "комедия", "боевик",
        "фантастика", "триллер", "мелодрама",
        "ужасы", "детектив", "приключения"
    ]

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    for i in range(0, len(genres), 2):
        row = [types.KeyboardButton(genres[i].title())]
        if i + 1 < len(genres):
            row.append(types.KeyboardButton(genres[i + 1].title()))
        keyboard.add(*row)

    # Кнопка для отмены
    keyboard.add(types.KeyboardButton("Отмена"))

    return keyboard
