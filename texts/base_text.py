from aiogram.utils import markdown

from misc.get_username import *
from config import emoji


def start_text(message: types.Message) -> list:
    text = [
        f" Привет, {define_username(message)}! {emoji['waving_hand']}\n\n",
        f"{markdown.hbold('Чтобы быстро начать парсинг файла')}:\n",
        f"1. Нажмите /parse.\n",
        f"2. Отправьте файл.\n"
        f"3. Нажмите на кнопку {emoji['left']}{'Обработать'}{emoji['right']} "
        f"или пришлите это сообщение текстом.\n\n",
    ]
    return text


def help_text() -> list:
    text = [
        f"Я умею парсить файлы и строить полезные графики."
    ]
    return text
