import logging
import os.path
import types

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandHelp, CommandStart, IDFilter

from loader import dp, db_manager
from texts.base_text import *
from filters.admin import AdminFilter
from misc.get_username import *
from keyboards.access_keyboard import *
from states.access_code import *
from utils.password_creator import generate_random_password


@dp.message_handler(CommandStart(), state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    logging.info(f"User {message.chat.id} requested {message.text}")
    text = start_text(message)
    db_manager.get_instance().create_user(message)
    await state.reset_state(with_data=True)

    if not db_manager.get_instance().check_if_user_has_access(message.chat.username, message.chat.id):
        await message.answer(f"У Вас пока нет доступа к функциям бота. "
                             f"Желаете ввести ключ доступа?", reply_markup=get_access_keyboard())
        await state.set_state(AccessCode.waiting_for_answer)
        return
    await message.answer("".join(text), reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(CommandHelp())
async def cmd_help(message: types.Message):
    logging.info(f"User {message.chat.id} requested {message.text}.")
    text = help_text()
    await message.answer("".join(text))


@dp.message_handler(AdminFilter(is_admin=True), commands='generate', state="*")
async def generate_passwords(message: types.Message) -> None:
    """Функция генерации паролей из файла password.txt.

    :param message: Телеграмм сообщение.
    :return: None
    """
    try:
        with open(os.path.join(os.getcwd(), '.', 'passwords.txt'), 'r') as file:
            for line in file.readlines():
                line = line.rstrip()
                if len(line) > 10:
                    query = f"""INSERT INTO codes (code) VALUES ('{line}');"""
                    db_manager.get_instance().execute_custom_query(query)
        await message.answer(f"Пароли были успешно вставлены.")
    except FileNotFoundError:
        with open(os.path.join(os.getcwd(), '.', 'passwords.txt'), 'w') as file:
            for _ in range(1000):
                file.write(generate_random_password() + '\n')
            await generate_passwords(message)
