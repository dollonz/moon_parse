import logging
import os.path
import time

import openpyxl
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import input_file

from loader import dp, bot, db_manager
from plots.bot_coin import create_bot_coin
from keyboards.plot_keyboards import *
from keyboards.access_keyboard import *
from config import emoji, PATH_TO_RESULT_REPORT, PATH_TO_DIAGRAMS
from states.plot import DiagramStates
from states.access_code import AccessCode


@dp.message_handler(commands=['plot'])
async def cmd_plot(message: types.Message, state: FSMContext) -> None:
    """Команда для начала процесса построения графика.

    Даёт пользователю клавиатуру, в которой он выбирает тип построения диаграммы.

    :param message: Сообщение от пользователя.
    :param state: Состояние, в котором находится пользователь.
    :return: None
    """

    if not db_manager.get_instance().check_if_user_has_access(message.chat.username, message.chat.id):
        await message.answer(f"К сожалению у Вас нет доступа к функциям бота. Желаете ввести ключ доступа?",
                             reply_markup=get_access_keyboard())
        await state.set_state(AccessCode.waiting_for_answer)
        return

    if os.path.exists(os.path.join(PATH_TO_RESULT_REPORT, f'{message.chat.id}.xlsx')):
        await message.answer("Выберите тип диаграммы.", reply_markup=get_choose_plot_keyboard())
        await DiagramStates.waiting_for_answer.set()
    else:
        await message.answer("Для начала обработайте файл командой /parse", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=DiagramStates.waiting_for_answer, content_types=['text'])
async def choose_diagram_type(message: types.Message, state: FSMContext) -> None:
    """Выбор типа построения диаграммы.

    :param message: Сообщение от пользователя.
    :param state: Состояние, в котором он находится.
    :return:
    """
    if message.text.lower() == 'нет':
        await state.finish()
        await message.answer('Можете отправить мне ещё файл для обработки.', reply_markup=types.ReplyKeyboardRemove())
        return
    elif message.text.lower() == 'стратегия-монеты':
        await message.answer('Подготавливаю данные. Пожалуйста, ожидайте...', reply_markup=types.ReplyKeyboardRemove())
        await building_strategy_coin_diagrams(message, state)
    elif message.text.lower() == 'математическое ожидание':
        await message.answer('Подготавливаю данные. Пожалуйста, ожидайте...', reply_markup=types.ReplyKeyboardRemove())
        await building_mean_plots(message, state)


async def building_strategy_coin_diagrams(message: types.Message, state: FSMContext) -> None:
    """Строит диаграмму стратегия-монета для каждого значения из 'название стратегии'.

    :param message: Сообщение от пользователя.
    :param state: Состояние, в котором находится пользователь.
    :return: None
    """
    channel_names = {
        'ru': 'Название стратегии',
        'en': 'ChannelName',
    }
    logging.info('Loading DataFrame')
    df = pd.read_excel(os.path.join(PATH_TO_RESULT_REPORT, f'{message.chat.id}.xlsx'))
    try:
        columns = df.columns
        clear_columns = [''.join(col.split()).lower() for ind, col in enumerate(columns)]

        if 'ChannelName'.lower() in clear_columns:
            channel_name = channel_names['en']
        else:
            channel_name = channel_names['ru']

        if 'profitbusd' in clear_columns:
            df = df[['Coin', columns[clear_columns.index('profitbusd')],
                     channel_name]].sort_values(channel_name)
            tmp_df = pd.pivot_table(df, values=columns[clear_columns.index('profitbusd')],
                                    index=['Coin'], columns=[channel_name], aggfunc=np.sum, fill_value=0.0)
        else:
            df = df[['Coin', columns[clear_columns.index('profitusdt')],
                     channel_name]].sort_values(channel_name)
            tmp_df = pd.pivot_table(df, values=columns[clear_columns.index('profitusdt')],
                                    index=['Coin'], columns=[channel_name], aggfunc=np.sum, fill_value=0.0)
    except KeyError as key:
        await message.answer(f"Не могу найти один из необходимых столбцов в отчёте. Останавливаю построение диаграммы.")
        await state.finish()
        logging.error(f"Error message: {key}")
        return

    col_names = tmp_df.columns
    logging.info(f'DataFrame is ready')

    for strategy_name in col_names:
        path = create_bot_coin(message, tmp_df, strategy_name)
        file = input_file.InputFile(path, filename=f'{strategy_name}.png')
        await message.answer_document(file)
    await message.answer(f"Все диаграммы успешно построены.\n"
                         f"Если хотите построить ещё, нажмите /plot.", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


async def building_mean_plots(message: types.Message, state: FSMContext) -> None:
    """Строит график мат. ожидания и возвращает путь к нему.

    :param file_path_to_table: Путь к файлу таблицы с данными.
    :return: Путь к файлу графика.
    """

    book = pd.read_excel(os.path.join(PATH_TO_RESULT_REPORT, f'{message.chat.id}.xlsx'))
    cols = ['dBTC', 'dMarket', 'dM24', 'd3h', 'd1h', 'd15m', 'd5m', 'd1m', 'dBTC1m']
    paths = []

    for row in cols:
        coin = row
        await message.answer(f"Загружаю {coin} график.")

        def mean_df(count_plus, count_minus, plus_value, minus_value):
            return abs(plus_value) * (count_plus / (count_plus + count_minus)) - \
                   abs(minus_value) * (count_minus / (count_plus + count_minus))

        df = book
        sorted_df = df.sort_values(by=coin).reset_index(drop=True)

        step = 0.05

        #print(sorted_df.head())

        start = float(sorted_df[coin][0])
        end = float(sorted_df[coin][len(sorted_df[coin])-1])
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
                    except ValueError as error:
                        logging.error(f'While making math: {error}')
                        continue
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

        try:
            path_to_save = os.path.join(PATH_TO_DIAGRAMS, str(message.chat.id))
        except FileNotFoundError:
            os.mkdir(os.path.join(PATH_TO_DIAGRAMS, str(message.chat.id)))
            path_to_save = os.path.join(PATH_TO_DIAGRAMS, str(message.chat.id))
        try:
            plt.savefig(os.path.join(path_to_save, f'{coin}.png'))
        except FileNotFoundError:
            os.mkdir(os.path.join(PATH_TO_DIAGRAMS, str(message.chat.id)))
            plt.savefig(os.path.join(path_to_save, f'{coin}.png'))

        plt.close('all')
        paths.append((os.path.join(path_to_save, f'{coin}.png'), coin))

    for path in paths:
        file = input_file.InputFile(path[0], filename=f'{path[1]}.png')
        await message.answer_document(file)
    await message.answer(f"Все диаграммы успешно построены.\n"
                         f"Если хотите построить ещё, нажмите /plot.", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()
