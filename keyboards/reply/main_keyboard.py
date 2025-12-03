from telebot import types


def main_keyboard() -> types.ReplyKeyboardMarkup:
    """
    Создает реплай-клавиатуру главного меню.

    :return: Объект клавиатуры
    :rtype: types.ReplyKeyboardMarkup
    """
    """Клавиатура главного меню"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                         input_field_placeholder="Выберете действие")
    keyboard.add(
        types.KeyboardButton(text="🔎 Поиск"),
        types.KeyboardButton(text="🔍 Поиск по рейтингу")

    )
    keyboard.add(
        types.KeyboardButton(text="🎬 История поиска"),
        types.KeyboardButton(text="📋 Буду смотреть")
    )

    return keyboard
