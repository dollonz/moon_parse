from aiogram.dispatcher.filters.state import State, StatesGroup


class ParseFile(StatesGroup):
    waiting_for_file = State()
