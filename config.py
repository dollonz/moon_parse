from aiogram import types
from environs import Env
import os

env = Env()
env.read_env()

emoji = {
    'left': u'\U000000AB',            #стрелка влево
    'right': u'\U000000BB',           #стрелка вправо
    'smiling_face': u'\U0001F60A',    #улыбающийся смайлик с розовыми щёчками
    'waving_hand': u'\U0001F44B',     #машущая рука
    'light_bulb': u'\U0001F4A1',      #лампочка
    'blue_diamond': u'\U0001F537',    #голубой ромб
}

commands = {
    "start": "Запустить бота",
    "parse": "Начать парсинг файла",
    "plot": "Построить график"
}


BOT_COMMANDS = [types.BotCommand(cmd, desc) for cmd, desc in commands.items()]

BOT_TOKEN = env.str("TELEGRAM_TOKEN")
ADMINS = [int(user_id) for user_id in env.list("ADMINS")]

PATH_TO_RESULT_REPORT = os.path.join(os.getcwd(), 'user_data/parse_result')
PATH_TO_DIAGRAMS = os.path.join(os.getcwd(), 'user_data/diagrams_result')
PATH_TO_DATABASE_INI = os.path.join(os.getcwd(), 'database.ini')
