from aiogram.types import InlineKeyboardMarkup, InlineQuery, InlineKeyboardButton


def check_user_access_kb() -> InlineKeyboardMarkup:
    """Клавиатура с 2 режимами на выбор.

    1. По имени пользователя.
    2. По коду доступа.

    :return: Клавиатура
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("Имя пользователя", callback_data="username")
            ],
            [
                InlineKeyboardButton("Код доступа", callback_data="access_code")
            ]
        ],
        row_width=1
    )


def back_kb() -> InlineKeyboardMarkup:
    """Клавиатура для возвращения на 1 пункт меню назад.

    :return: Клавиатура
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("Назад", callback_data='back')
            ]
        ]
    )


def yes_kb() -> InlineKeyboardMarkup:
    """Клавиатура, где требуется получить ответ да или нет.

    :return: Клавиатура
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("Да", callback_data='yes')
            ],
            [
                InlineKeyboardButton('Назад', callback_data='back')
            ]
        ]
    )
