from telebot.types import Message

from config_data.config import DEFAULT_COMMANDS
from loader import bot


@bot.message_handler(commands=["help"])
def bot_help(message: Message):
    """
    Обработчик команды /help.

    Отправляет список доступных команд.

    :param message: Входящее сообщение от пользователя
    :type message: Message
    """
    text = [f"/{command} - {desk}" for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, "\n".join(text))
