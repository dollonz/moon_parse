from aiogram import types


def get_plot_inline_keyboard() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        row_width=1,
        inline_keyboard=[
            [
                types.InlineKeyboardButton("Построить график", callback_data='build')
            ]
        ]
    )


def get_choose_plot_keyboard() -> types.ReplyKeyboardMarkup:
    """Клавиатура, появляющаяся после обработки отчёта. Предлагает на выбор 3 варианта
    построения диаграммы.

    :return: Keyboard with 3 buttons (variants of plots).
    """

    return types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text="Стратегия-монеты")
            ],
            [
                types.KeyboardButton(text="Математическое ожидание")
            ],
            [
                types.KeyboardButton(text="Нет")
            ]
        ],
        resize_keyboard=True
    )
