from telebot import types


def movie_actions_keyboard(watched: bool = False) -> types.ReplyKeyboardMarkup:
    """
    Создает реплай-клавиатуру действий с фильмом.

    :param watched: Отмечен ли фильм как просмотренный
    :type watched: bool
    :return: Объект клавиатуры
    :rtype: types.ReplyKeyboardMarkup
    """
    """Клавиатура действий с фильмом"""
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True
    )

    if watched:
        keyboard.add(types.KeyboardButton("✅ Просмотрено"))
    else:
        keyboard.add(types.KeyboardButton("✔️ Отметить просмотренным"))

    keyboard.add(
        types.KeyboardButton("📌 Добавить в 'Смотреть позже'"),
        types.KeyboardButton("🏠 Главное меню")
    )

    return keyboard