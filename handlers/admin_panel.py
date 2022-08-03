import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils import markdown
from loader import dp, db_manager
from filters.admin import AdminFilter
from keyboards.check_inline_kb import *
from texts.admin_panel_text import *
from states.admin import CheckUserState


@dp.message_handler(AdminFilter(is_admin=True), commands='check', state="*")
async def check_if_user_has_access(message: types.Message, state: FSMContext) -> None:
    """Отправляет сообщение с inline клавиатурой, чтобы можно было проверить доступ у пользователя.

    :param message: Сообщение от пользователя.
    :return: None
    """

    await state.reset_state(with_data=False)
    await message.answer('\n'.join(check_if_user_has_access_text), reply_markup=check_user_access_kb())


@dp.callback_query_handler(AdminFilter(is_admin=True), lambda x: x.data == 'username')
async def check_access_by_username(call: types.CallbackQuery, state: FSMContext) -> None:
    """Переводит админа в состояние ожидания имени пользователя для проверки.

    :param call: Информация с тг кнопок.
    :param state: Состояние, в котором находится пользователь.
    :return: None
    """

    await state.set_state(CheckUserState.waiting_for_username)
    await call.message.edit_text('\n'.join(check_access_by_username_text), reply_markup=back_kb())


@dp.callback_query_handler(AdminFilter(is_admin=True), lambda x: x.data == 'access_code')
async def check_access_by_username(call: types.CallbackQuery, state: FSMContext) -> None:
    """Переводит админа в состояние ожидания кода доступа для проверки.

    :param call: Информация с тг кнопок.
    :param state: Состояние, в котором находится пользователь.
    :return: None
    """

    await state.set_state(CheckUserState.waiting_for_code)
    await call.message.edit_text('\n'.join(check_access_by_code_text), reply_markup=back_kb())


@dp.callback_query_handler(AdminFilter(is_admin=True), lambda x: x.data == 'back',
                           state=CheckUserState)
async def back_to_check_if_user_has_access(call: types.CallbackQuery, state: FSMContext) -> None:
    """Возвращает администратора к выбору режима проверки.

    :param call: Информация с тг кнопок.
    :param state: Состояние, в котором находится пользователь.
    :return: None
    """

    await state.reset_state(with_data=True)
    await call.message.edit_text('\n'.join(check_if_user_has_access_text), reply_markup=check_user_access_kb())


@dp.message_handler(AdminFilter(is_admin=True), state=CheckUserState.waiting_for_code, content_types='text')
async def send_code_to_db_to_check_access(message: types.Message, state: FSMContext) -> None:
    """Отправляет код на проверку в БД.

    :param message: Сообщение от пользователя.
    :param state: Состояние, в котором находится пользователь.
    :return: None
    """

    code = message.text.strip()
    if db_manager.get_instance().check_if_code_is_occupied(code):
        logging.info(f"Code is occupied by user.")
        username = db_manager.get_instance().get_username_by_code(code)
        await message.answer(f"Пользователь {'@' + username} использует этот код доступа.\n\n"
                             f"Желаете забрать ключ доступа?", reply_markup=yes_kb())
        await state.set_state(CheckUserState.waiting_to_remove_user)
    else:
        await message.answer(f"Данный код доступа никому не принадлежит. Вы можете его использовать.",
                             reply_markup=types.ReplyKeyboardRemove())
        await state.reset_state(with_data=True)


@dp.message_handler(AdminFilter(is_admin=True), state=CheckUserState.waiting_for_username, content_types='text')
async def send_username_to_db_to_check_access(message: types.Message, state: FSMContext) -> None:
    """Отправляет имя пользователя в БД для проверки доступа.

    :param message: Сообщение от пользователя.
    :param state: Состояние, в котором находится пользователь.
    :return: None
    """

    username = message.text.strip()
    if username.startswith('@'):
        username = username[1:]

    if db_manager.get_instance().check_access_by_username(username):
        await message.answer(f"У пользователя {'@' + username} есть доступ к боту.\n"
                             f"Его код доступа: {db_manager.get_instance().get_access_code_by_username(username)}\n\n"
                             f"Желаете забрать доступ?",
                             reply_markup=yes_kb())
        await state.set_state(CheckUserState.waiting_to_remove_user)
    else:
        await message.answer(f"У пользователя {'@' + username} нет доступа.\n",
                             reply_markup=back_kb())
        await state.set_state(CheckUserState.waiting_to_give_access)


@dp.callback_query_handler(AdminFilter(is_admin=True), lambda x: x.data == 'yes', state=CheckUserState)
async def remove_access(call: types.CallbackQuery, state: FSMContext) -> None:
    """Забирает доступ к боту у пользователя.

    :param call: Информация с тг кнопок.
    :param state: Состояние, в котором находится пользователь.
    :return: None
    """

    text = call.message.text
    beg_index = text.find('@')
    end_index = text[beg_index+1:].find(' ')
    username = text[beg_index+1:beg_index + end_index + 1]

    db_manager.get_instance().remove_access_by_username(username)
    await call.message.edit_text(f"Успешно ограничен доступ пользователю {'@' + username}.",
                                 reply_markup=back_kb())
