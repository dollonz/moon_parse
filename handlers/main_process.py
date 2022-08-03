import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from states.access_code import AccessCode
from states.parse import ParseFile
from parsers.main_parser import start_parse
from loader import dp, bot, db_manager
from texts.parse_text import get_cmd_parse_text
from keyboards.parse_keyboards import *
from keyboards.access_keyboard import *


@dp.message_handler(commands=['parse'])
async def cmd_parse(message: types.Message, state: FSMContext):
    """ Обработчик команды /parse.

    Устанавливает состояние ожидания файла для обработки.

    :param message: Сообщение от пользователя.
    :param state: Состояние, в котором находится пользователь.
    :return:
    """

    logging.info(f"User {message.chat.id} requested {message.text}")
    if not db_manager.get_instance().check_if_user_has_access(message.chat.username, message.chat.id):
        await message.answer(f"К сожалению у Вас нет доступа к функциям бота. Желаете ввести ключ доступа?",
                             reply_markup=get_access_keyboard())
        await state.set_state(AccessCode.waiting_for_answer)
        return

    text = get_cmd_parse_text()

    await message.answer("".join(text), reply_markup=get_file_waiting_keyboard())
    await ParseFile.waiting_for_file.set()


@dp.message_handler(state=ParseFile.waiting_for_file, content_types=['document', 'text'])
async def process_parse_state(message: types.Message, state: FSMContext):
    """ Функция приема документа для обработки.

    Также контролирует выход из состояния ожидания файла.

    :param message: Сообщение от пользователя.
    :param state: Состояние, в котором находится пользователь.
    :return:
    """

    if message.content_type == 'document':
        logging.info(f"User {message.chat.id} sending some data in waiting_for_file state.")
        await message.answer(f"Загружаю Ваш файл...",
                             reply_markup=get_file_waiting_keyboard())
        document = await bot.get_file(message.document.file_id)
        await state.set_data({str(message.chat.id): document.file_path})
        await message.answer(f"Файл успешно загружен!")
    elif message.content_type == 'text' and message.text.lower() == 'обработать':
        logging.info(f"User {message.chat.id} start parse file.")
        try:
            await message.answer(f"Начинаю обработку...",
                                 reply_markup=types.ReplyKeyboardRemove())
            await start_parse((await state.get_data(str(message.chat.id)))[str(message.chat.id)], message, state)
        except TypeError:
            await message.answer(f"Повторите отправку файла.", reply_markup=get_file_waiting_keyboard())
            return
        await state.finish()
    elif message.content_type == 'text' and message.text.lower() == 'отмена':
        logging.info(f"User {message.chat.id} exiting from waiting_for_file state.")
        await message.answer(f"Отменяю обработку.", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    else:
        await message.answer(f"Отправьте мне файл для обработки или напишите «отмена», чтобы выйти в меню.",
                             reply_markup=get_file_waiting_keyboard())
