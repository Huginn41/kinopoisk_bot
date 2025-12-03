from loader import bot
import handlers  # noqa
from utils.set_bot_commands import set_default_commands

if __name__ == "__main__":
    """
    Точка входа в приложение.

    Настраивает команды и запускает бота в режиме долгих опросов.
    """
    set_default_commands(bot)
    bot.infinity_polling()
