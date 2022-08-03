from aiogram.dispatcher.filters.state import State, StatesGroup


class DiagramStates(StatesGroup):
    waiting_for_answer = State()
