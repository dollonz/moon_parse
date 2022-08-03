from aiogram.dispatcher.filters.state import State, StatesGroup


class CheckUserState(StatesGroup):
    waiting_for_username = State()
    waiting_for_code = State()
    waiting_to_remove_user = State()
    waiting_to_give_access = State()
