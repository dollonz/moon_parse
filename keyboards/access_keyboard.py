from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_access_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура, которая высвечивается, когда у пользователя нет доступа к боту.

    :return: Клавиатура
    """

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton("Да")
            ],
            [
                KeyboardButton("Где мне его получить?")
            ]
        ],
        resize_keyboard=True
    )


def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с одной кнопкой: отмена, чтобы вернуться к клавиатуре get_access_keyboard

    :return: Клавиатура
    """

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton("Назад")
            ]
        ],
        resize_keyboard=True
    )
