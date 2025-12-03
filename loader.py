from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
from telebot.custom_filters import StateFilter


storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
"""
Экземпляр бота, используемый во всем проекте.
"""
bot.add_custom_filter(StateFilter(bot))