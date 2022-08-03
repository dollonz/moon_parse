import logging

from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from loader import db_manager, dp
from states.access_code import AccessCode
from keyboards.access_keyboard import *


@dp.message_handler(Text(equals='да', ignore_case=True), state=AccessCode.waiting_for_answer)
async def change_to_getting_code_state(message: types.Message, state: FSMContext) -> None:
    """Переводит в состояние принятия кода доступа от пользователя.

    :param message: Сообщение от пользователя.
    :param state: Состояние, в котором находится пользователь.
    :return: None
    """

    await message.answer(f"Введите ключ доступа.", reply_markup=get_back_keyboard())
    await state.set_state(AccessCode.waiting_for_code)


@dp.message_handler(Text(equals='где мне его получить?', ignore_case=True), state=AccessCode.waiting_for_answer)
async def answer_instruction_to_get_access_code(message: types.Message, state: FSMContext) -> None:
    """Выводит пользователю инструкцию, как получить доступ к боту.

    :param message: Сообщение от пользователя.
    :param state: Состояние, в котором находится пользователь.
    :return: None
    """

    await message.answer(f"Доступ можно получить у админа. Он Вам выдаст код, состоящий из 24 символов. "
                         f"Его нужно будет отправить мне.", reply_markup=get_access_keyboard())


@dp.message_handler(Text(equals='назад ', ignore_case=True), state=AccessCode.waiting_for_code)
async def return_ro_waiting_for_answer_state(message: types.Message, state: FSMContext) -> None:
    """

    :param message:
    :param state:
    :return:
    """

    await message.answer("Желаете попробовать снова?", reply_markup=get_access_keyboard())
    await state.set_state(AccessCode.waiting_for_answer)


@dp.message_handler(state=AccessCode.waiting_for_code, content_types='text')
async def check_code_for_valid(message: types.Message, state: FSMContext) -> None:
    """Если код правильный, то выдаёт доступ пользователю, закрепляя за ним код в БД.

    :param message: Сообщение от пользователя.
    :param state: Состояние, в котором находится пользователь.
    :return: None
    """

    code = message.text.strip()
    if code.lower() == 'назад':
        await return_ro_waiting_for_answer_state(message, state)
        return

    if len(code) != 24:
        await message.answer(f"Код введён некорректно.", reply_markup=get_back_keyboard())
        return

    text, success = db_manager.get_instance().check_access_code(message, code)

    if not success:
        await message.answer(text, reply_markup=get_back_keyboard())
    else:
        await message.answer(text, reply_markup=types.ReplyKeyboardRemove())
        await state.reset_state(with_data=True)
