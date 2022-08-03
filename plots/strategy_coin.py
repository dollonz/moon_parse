import logging
import os.path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from aiogram import types
from config import PATH_TO_DIAGRAMS


def create_strategy_coin_diagram(message: types.Message, data: pd.DataFrame, strategy_name: str) -> os.path:
    """Функция построения диаграммы типа стратегия-монета.

    :param message: Сообщение от пользователя.
    :param data: Данные для построения.
    :param strategy_name: Название стратегии.
    :return: Путь к диаграмме на компьютере.
    """

    fig, ax = plt.subplots(figsize=(15, 48))

    clear_df = data[strategy_name].where(lambda x: x != 0.0).dropna()

    coins = clear_df.index
    y_pos = np.arange(len(coins))
    profit = clear_df
    positive = np.array([x for x in profit if x >= 0.0])
    positive_coins = coins[:len(positive)]
    negative = np.array([x for x in profit if x < 0.0])
    negative_coins = coins[len(positive):]

    ax.barh(positive_coins, positive, align='edge', color='green', height=1)
    ax.barh(negative_coins, negative, align='edge', color='red', height=1)
    ax.set_yticks(y_pos, labels=coins)
    ax.tick_params(axis='y', which='major', labelsize=8)
    ax.tick_params(axis='y', which='minor', labelsize=8)
    ax.invert_yaxis()
    ax.set_title(f'{strategy_name}')
    ax.grid()

    try:
        path_to_save = os.path.join(PATH_TO_DIAGRAMS, str(message.chat.id))
    except FileNotFoundError:
        os.mkdir(os.path.join(PATH_TO_DIAGRAMS, str(message.chat.id)))
        path_to_save = os.path.join(PATH_TO_DIAGRAMS, str(message.chat.id))

    plt.savefig(os.path.join(path_to_save, f'{strategy_name}.png'))
    plt.close('all')
    return os.path.join(path_to_save, f'{strategy_name}.png')
