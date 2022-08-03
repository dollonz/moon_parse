import numpy as np
import pandas as pd
import time
import matplotlib.pyplot as plt
import openpyxl
import os

from aiogram.types import message

from config import PATH_TO_DIAGRAMS


def get_mean_plot(file_path_to_table: str) -> os.path:
    """Строит график мат. ожидания и возвращает путь к нему.

    :param file_path_to_table: Путь к файлу таблицы с данными.
    :return: Путь к файлу графика.
    """

    book = pd.read_excel(file_path_to_table)
    cols = ['dBTC', 'dMarket', 'dM24', 'd3h', 'd1h', 'd15m', 'd5m', 'd1m', 'dBTC1m']
    #cols = ['dBTC', 'dMarket', 'dM24', 'd3h', 'd1h', 'd15m', 'd5m', 'd1m', 'dBTC1m', 'MAvg', 'EMA', 'BTC', 'MIN', 'MAX']

    for row in cols:
        coin = row
        print(coin)

        def mean_df(count_plus, count_minus, plus_value, minus_value):
            return abs(plus_value) * (count_plus / (count_plus + count_minus)) - \
                   abs(minus_value) * (count_minus / (count_plus + count_minus))

        df = book
        sorted_df = df.sort_values(by=coin).reset_index(drop=True)

        step = 0.05

        #print(sorted_df.head())

        start = float(sorted_df[coin][0])
        end = float(sorted_df[coin][1191])
        math_means = []
        distance = []

        while start <= end:
            # Шагаем
            two_start = float(start) + float(step)
            two_start = round(two_start, 2)

            plus_counts = 0
            minus_counts = 0
            plus_value = 0
            minus_value = 0
            for i in range(0, len(sorted_df[coin])):
                if start < sorted_df[coin][i] <= two_start:
                    # print('Count of data: ', i)
                    try:
                        if float(sorted_df['ProfitUSDT'][i]) >= 0:
                            plus_counts += 1
                            plus_value += float(sorted_df['ProfitUSDT'][i])

                        else:
                            minus_counts += 1
                            minus_value += float(sorted_df['ProfitUSDT'][i])
                    except KeyError:
                        if float(sorted_df['ProfitAbs'][i].rstrip()[:-1:]) >= 0:
                            plus_counts += 1
                            plus_value += float(sorted_df['ProfitAbs'][i].rstrip()[:-1:])

                        else:
                            minus_counts += 1
                            minus_value += float(sorted_df['ProfitAbs'][i].rstrip()[:-1:])
            if plus_counts + minus_counts != 0:
                math_mean = mean_df(plus_counts, minus_counts, plus_value, minus_value)

            else:
                math_mean = 0
            math_means += [math_mean]
            distance += [str(start) + ' to ' + str(two_start)]
            # print('Диапазон: ', start,'-',two_start,'    ', 'Мат.ожидание: ',math_mean)

            start += float(step)
            start = round(start, 2)

        # print(distance)

        colors = ['g' if x > 0 else 'r' for x in math_means]
        plt.figure(figsize=(
        10, len(distance) // 4 + 1))  # Задаёт размер итогового графика. Надо понять, как сделать его динамическим
        plt.title(coin)
        plt.grid()
        plt.barh(distance, math_means, color=colors)
        plt.savefig('math.png')

        try:
            path_to_save = os.path.join(PATH_TO_DIAGRAMS, str(message.chat.id))
        except FileNotFoundError:
            os.mkdir(os.path.join(PATH_TO_DIAGRAMS, str(message.chat.id)))
            path_to_save = os.path.join(PATH_TO_DIAGRAMS, str(message.chat.id))

        plt.savefig(os.path.join(path_to_save, f'{coin}.png'))
        plt.close('all')
        return os.path.join(path_to_save, f'{coin}.png')

