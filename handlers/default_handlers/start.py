from telebot.types import Message

from keyboards.reply.main_keyboard import main_keyboard
from loader import bot


@bot.message_handler(commands=["start"])
def start_message(message: Message):
    """
    Обработчик команды /start.

    Отправляет приветственное сообщение и главное меню.

    :param message: Входящее сообщение от пользователя
    :type message: Message
    """
    welcome_text = """
    Добро пожаловать в бот для поиска фильмов!

    Как использовать:
    1. 🔎Поиск - для поиска фильма/сериала по названию
    2. 🔍По рейтингу - для поиска по рейтингу
    3. 📋Буду смотреть - открыть сохраненный список
    4. 🎬История - просмотр истории поиска
    """
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=main_keyboard(),
    )
