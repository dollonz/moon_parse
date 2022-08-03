import os
import pandas as pd




def get_mean_plot(df):
    """Строит график мат. ожидания и возвращает путь к нему.

    :param file_path_to_table: Путь к файлу таблицы с данными.
    :return: Путь к файлу графика.
    """

    res = [[], [], [], []]
    cols = ['dBTC', 'dMarket', 'dM24', 'd3h', 'd1h', 'd15m', 'd5m', 'd1m', 'dBTC1m']


    for row in cols:
        coin = row

        def mean_df(count_plus, count_minus, plus_value, minus_value):
            return abs(plus_value) * (count_plus / (count_plus + count_minus)) - \
                   abs(minus_value) * (count_minus / (count_plus + count_minus))

        sorted_df = df.sort_values(by=coin).reset_index(drop=True)

        step = 0.05


        start = float(sorted_df[coin][0])
        end = float(sorted_df[coin][len(sorted_df[coin])-1])
        math_means = []
        distance = []
        list_par = []
        list_strat = []

        while start <= end:
            # Шагаем
            two_start = float(start) + float(step)
            two_start = round(two_start, 2)
            strat = ''

            plus_counts, minus_counts, plus_value, minus_value = 0, 0, 0, 0
            for i in range(0, len(sorted_df[coin])):
                #print(i, sorted_df[coin][i])
                if start <= float(sorted_df[coin][i]) <= two_start:
                    #print('Count of data: ', i)
                    strat = sorted_df['Comment'][i].split()[0]

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
            list_strat += [strat]
            distance += [str(start) + '...' + str(two_start)]
            list_par += [row]

            start += float(step)
            start = round(start, 2)
        res[0].extend(list_strat)
        res[1].extend(list_par)
        res[2].extend(distance)
        res[3].extend(math_means)
    return res






