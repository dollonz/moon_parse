import logging
import os.path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from aiogram import types
from config import PATH_TO_DIAGRAMS


def create_bot_coin(message: types.Message, data: pd.DataFrame, channel_name: str) -> os.path:
    """Строит диаграмму типа: стратегия-монета.

    Подсчёт выполняется для конкретного значения из столбца ChannelName (например, #d0019).
    Строки - название монеты, значения - сумма по столбцу Profit BUSD или Profit USTD.

    :param message: Сообщение от telegram.
    :param data: DataFrame, в котором просуммированы соответствующие значения.
    :param channel_name: Индекс текущего значения ChannelName (например: #d0019)
    :return: None
    """

    fig, ax = plt.subplots(figsize=(15, 48))

    clear_data = data[channel_name].where(lambda x: x != 0.0).dropna()

    coins = clear_data.index
    y_pos = np.arange(len(coins))
    profit = clear_data
    print(profit)
    print(coins)

    col = np.where(profit < 0.0, 'red', 'green')

    ax.barh(coins, profit, color=col, height=0.8)
    ax.set_yticks(y_pos, labels=coins)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.tick_params(axis='y', which='minor', labelsize=8)
    ax.invert_yaxis()
    ax.set_title(f'{channel_name}')
    ax.grid()

    try:
        path_to_save = os.path.join(PATH_TO_DIAGRAMS, str(message.chat.id))
    except FileNotFoundError:
        os.mkdir(os.path.join(PATH_TO_DIAGRAMS, str(message.chat.id)))
        path_to_save = os.path.join(PATH_TO_DIAGRAMS, str(message.chat.id))

    try:
        plt.savefig(os.path.join(path_to_save, f'{channel_name}.png'))
    except FileNotFoundError:
        os.mkdir(os.path.join(path_to_save))
        plt.savefig(os.path.join(path_to_save, f'{channel_name}.png'))
    plt.close('all')
    return os.path.join(path_to_save, f'{channel_name}.png')
