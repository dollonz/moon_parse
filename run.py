import logging
import os
import shutil

logging.basicConfig(level=logging.INFO)

import handlers

from aiogram import Dispatcher, executor

from loader import dp, db_manager
from config import PATH_TO_DIAGRAMS, PATH_TO_RESULT_REPORT
from utils.set_bot_commands import set_default_commands


async def clear_user_data(*args, **kwargs) -> None:
    """Удаляет папки и файлы с отчётами и диаграммами при остановке бота.

    :return: None
    """

    for file in os.listdir(PATH_TO_RESULT_REPORT):
        if os.path.isdir(os.path.join(PATH_TO_RESULT_REPORT, file)):
            shutil.rmtree(os.path.join(PATH_TO_RESULT_REPORT, file))
        else:
            os.remove(os.path.join(PATH_TO_RESULT_REPORT, file))

    for directory in os.listdir(PATH_TO_DIAGRAMS):
        if os.path.isdir(os.path.join(PATH_TO_DIAGRAMS, directory)):
            shutil.rmtree(os.path.join(PATH_TO_DIAGRAMS, directory))
        else:
            os.remove(os.path.join(PATH_TO_DIAGRAMS, directory))


async def on_startup(dp: Dispatcher) -> None:
    """ Устанавливает базовые команды при запуске бота.

    :param dp: Диспетчер обновлений серверов телеграмма.
    :return: None
    """

    if not os.path.exists(os.path.join(os.getcwd(), 'user_data')):
        logging.info("Creating user_data folder.")
        os.mkdir(os.path.join(os.getcwd(), 'user_data'))

    if not os.path.exists(PATH_TO_DIAGRAMS):
        logging.info("Creating user_data/diagrams_result folder")
        os.mkdir(PATH_TO_DIAGRAMS)

    if not os.path.exists(PATH_TO_RESULT_REPORT):
        logging.info("Creating user_data/parse_result folder")
        os.mkdir(PATH_TO_RESULT_REPORT)

    db_manager.get_instance().create_table()

    await set_default_commands(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=clear_user_data)
