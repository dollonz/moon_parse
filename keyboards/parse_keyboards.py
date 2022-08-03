from aiogram import types


def get_file_waiting_keyboard() -> types.ReplyKeyboardMarkup:
    """ Клавиатура, которая отображается во время ожидания файла для парсинга.

    :return: Клавиатура с одной кнопкой: обработать
    """

    return types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="Обработать")
            ],
            [
                types.KeyboardButton(text="Отмена")
            ]
        ],
        resize_keyboard=True
    )
