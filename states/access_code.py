from aiogram.dispatcher.filters.state import State, StatesGroup


class AccessCode(StatesGroup):
    waiting_for_answer = State()
    waiting_for_code = State()
