from telebot.types import BotCommand
from config_data.config import DEFAULT_COMMANDS


def set_default_commands(bot) -> None:
    """
    Устанавливает стандартные команды бота.

    :param bot: Экземпляр бота
    :type bot: TeleBot
    """
    bot.set_my_commands(
        [BotCommand(*i) for i in DEFAULT_COMMANDS]
    )
