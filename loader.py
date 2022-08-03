from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from utils.database_manager import DBManager
from filters.admin import AdminFilter

import config

""" Структура хранилища следующая:
user_id_1: [document_1, document_2, ...],
user_id_2: [document_1, document_2, ...],
...
user_id_n: [document_1, document_2, ...]
"""
storage = RedisStorage2()

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

# Подключение своих фильтров
dp.filters_factory.bind(AdminFilter)

db_manager = DBManager.get_instance()
