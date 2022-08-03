import logging
import os.path
import time
import typing

import aiogram.utils.exceptions
import pandas as pd
from pandas.io.excel import ExcelWriter

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import input_file

from loader import bot
from config import PATH_TO_RESULT_REPORT
from parsers.joined_sell import parse_joined_sell
from parsers.EMA import parse_EMA_comment
from parsers.drops_detection import parse_DropsDetection_comment
from parsers.moon_hook_plus_spreaddetection import parse_hook_long_depth_comment, parse_moonstrike_comment
from parsers.moonshot import parse_moonshot
from parsers.pump_plus_strike_detection import parse_pumpdetection_plus_strikedetection
from parsers.puvp_detection import parse_PuvpDetection
from parsers.stread_detection import parse_StreadDetection
from parsers.creat_3_list import get_mean_plot


async def get_headers(file_path: os.path, message: types.Message, state: FSMContext) -> list:
    """ Пробегается по файлу и для каждой строки записывает стратегию.

    :param file_path: Путь к файлу, который обрабатываем.
    :param message: Сообщение от пользователя
    :return: [strategy_1, strategy_2, ...]
    """
    result = []
    unknown_comments = set()
    with open(file_path, 'r') as file:
        _ = file.readline()  # Это строка Binance Report - она не нужна
        headers = [header.strip() for header in file.readline().rstrip().split('\t')]
        try:
            comment_index = headers.index('Comment')
        except ValueError:
            await message.answer(f"Файл не соответствует шаблону.", reply_markup=types.ReplyKeyboardRemove())
            await state.finish()
            return
        for ind, line in enumerate(file.readlines()):
            line = line.rstrip().split('\t')

            try:
                comment = line[comment_index].lstrip()
            except IndexError:
                continue

            # Получаем стратегию и оставшийся комментарий
            if comment[:60].find(';') != -1:
                strategy, comment = comment.split(';', maxsplit=1)
            elif comment[:60].find(':') != -1:
                strategy, comment = comment.split(':', maxsplit=1)
            else:
                result.append('')
                len_before_adding = len(unknown_comments)
                unknown_comments.add(comment[:100])
                len_after_adding = len(unknown_comments)
                if len_before_adding != len_after_adding:
                    try:
                        print(comment)
                        await message.answer(f"Не могу распознать комментарий на {ind + 3} строке входного файла:\n\n"
                                             f"{comment[:30]}...", reply_markup=types.ReplyKeyboardRemove())
                    except:
                        await message.answer(f"Произошла ошибка при поиске названий стратегий. Возможно, "
                                             f"какая-то стратегия не была распознана.\n\n"
                                             f"Ошибка на {ind + 3} строке файла.",
                                             reply_markup=types.ReplyKeyboardRemove())
                continue

            result.append(strategy)

    return result


async def download_file(file_path: str, message: types.Message) -> str:
    """Скачать файл с серверов telegram.

    Скачивает в папку ./data/user_id/

    :param file_path: Путь к файлу на тг сервере.
    :param message: Сообщение от пользователя.
    :return: Путь к файлу на компьютере
    """
    if not os.path.exists(os.path.join(os.getcwd(), 'data')):
        os.mkdir(os.path.join(os.getcwd(), 'data'))
    if not os.path.exists(os.path.join(os.getcwd(), 'data', str(message.chat.id))):
        os.mkdir(os.path.join(os.getcwd(), 'data', str(message.chat.id)))

    extension_of_file = file_path.split('.')[-1]
    await bot.download_file(file_path, os.path.join(os.getcwd(), 'data', str(message.chat.id),
                                                    'report.' + extension_of_file))
    return os.path.join(os.getcwd(), 'data', str(message.chat.id), 'report.' + extension_of_file)


def get_func_to_parse(strategy_name: str):
    """Возвращает объект функции, которая будет обрабатывать комментарий определенного вида.

    :param strategy_name: Название стратегии в начале комментария.
    :return: function: Функция, которую можно вызвать в программе.
    """

    if strategy_name.find('dropsdetection') != -1:
        return parse_DropsDetection_comment
    elif strategy_name.find('joined sell') != -1:
        return parse_joined_sell
    elif strategy_name.find('moonstrike') != -1:
        return parse_moonstrike_comment
    elif strategy_name.find('moonshot') != -1:
        return parse_moonshot
    elif strategy_name.find('spreaddetection') != -1:
        return parse_StreadDetection
    elif strategy_name.find('emadetection') != -1:
        return parse_EMA_comment
    elif strategy_name.find('autodetection') != -1:
        return parse_moonstrike_comment
    elif strategy_name.find('pumpdetection') != -1:
        return parse_PuvpDetection
    elif strategy_name.find('hook long depth') != -1:
        return parse_hook_long_depth_comment
    else:
        return None


async def start_parse(file_path: str, message: types.Message, state: FSMContext) -> os.path:
    """ Главная функция обработки файла.

    Получает все заголовки и создаёт табличку из отчёта.

    :param file_path: Путь к файлу, который обрабатываем.
    :param message: Сообщение, полученное от пользователя.
    :param state: Состояние, в котором находится пользователь.
    :return: os.path: Путь к табличке, которая получена в результате обработки
    """

    await message.answer("Начинаю предварительный просмотр файла.", reply_markup=types.ReplyKeyboardRemove())
    file_on_pc = await download_file(file_path, message)
    strategies = await get_headers(file_on_pc, message, state)

    await message.answer(f"В файле обнаружено: {len(set(strategies))} стратегий.\n"
                         f"Начинаю создание таблицы...")

    result = pd.DataFrame()

    with open(file_on_pc, 'r') as file:
        _ = file.readline()
        headers = [header.strip() for header in file.readline().strip().split('\t')]
        print(headers)
        if "ProfitUSDT" in headers:
            index_profite = headers.index("ProfitUSDT")
        else:
            index_profite = headers.index("Profit USDT")
        comment_index = headers.index('Comment')
        dct_pol, dct_otr, dct_profit, res_dict = {}, {}, {}, {"Название стратегии": [], "Монета": [],\
                                                              "Число положительных сделок": [], "Профит": [],\
                                                              "Число отрицательных сделок": []}
        for ind, line in enumerate(file.readlines()):
            line = line.strip().split('\t')
            try:
                strategy_parse = strategies[ind].lower()
            except IndexError:
                logging.warning(f"IndexError in start_parse function. {ind}/{len(strategies)}")
                continue
            try:
                key = line[0] + line[comment_index].split()[0]
                #print(ind, key, len(line))
                if float(line[index_profite]) > 0:
                    dct_pol[key] = dct_pol.get(key, 0) + 1
                else:
                    dct_otr[key] = dct_otr.get(key, 0) + 1
                dct_profit[key] = dct_profit.get(key, 0) + float(line[index_profite])


            except TypeError as error:
                logging.error(f"Error in 164 - 167 main_parser.py")
                logging.error(f"Error message: {error}")

            try:
                parsed_comment = get_func_to_parse(strategy_parse)(line[comment_index])
                print(parsed_comment)
                tmp_df = pd.DataFrame([line + parsed_comment[0]], columns=headers + parsed_comment[1])
            except TypeError as error:
                logging.error(f"I don't know how to parse: '{strategy_parse}'")
                logging.error(f"Error message: {error}")
                continue
            except IndexError:
                continue
            except ValueError as error:
                logging.error(f"ValueError while parsing {strategy_parse}")
                logging.error(f"Error message: {error}")
                continue

            if result.empty:
                result = tmp_df
            else:
                try:
                    result = pd.concat([result, tmp_df], ignore_index=True, verify_integrity=True)
                except pd.errors.InvalidIndexError as error:
                    logging.error(f"Error while parsing {strategy_parse}.\n"
                                  f"Message: {error}")
                    continue
        for key, value in dct_pol.items():
            try:
                res_dict["Название стратегии"].append(key.split()[1])
                res_dict["Монета"].append(key.split()[0])
                res_dict["Число положительных сделок"].append(value)
                res_dict["Профит"].append(dct_profit[key])
                res_dict["Число отрицательных сделок"].append(dct_otr.get(key, 0))
            except IndexError:
                 logging.error(f'{key} - {value}')
        result_second = pd.DataFrame.from_dict(res_dict)
        list_math = get_mean_plot(result)
        dct_3_list = {"Название стратегии": list_math[0], "Параметр": list_math[1],\
                      "Диапазон": list_math[2], "Математическое ожидание": list_math[3]}
        result_third = pd.DataFrame.from_dict(dct_3_list)
    await create_xlsx(result, result_second, result_third, message)


async def create_xlsx(data1: pd.DataFrame, data2: pd.DataFrame, data3: pd.DataFrame, message: types.Message) -> None:
    """Создаёт табличку из обработанного отчёта и отправляет пользователю.

    :param data1: Обработанные данные.
    :param message: Сообщение от пользователя.
    """
    data1.to_excel(os.path.join(PATH_TO_RESULT_REPORT, f'{message.chat.id}.xlsx'))
    #get_mean_plot(os.path.join(PATH_TO_RESULT_REPORT, f'{message.chat.id}.xlsx'))
    with ExcelWriter(os.path.join(PATH_TO_RESULT_REPORT, f'{message.chat.id}.xlsx'), mode="w") as writer:
        data1.to_excel(writer, sheet_name="Отчет", index=False)
        data2.to_excel(writer, sheet_name="Профит", index=False)
        data3.to_excel(writer, sheet_name="Мат.Ожидания", index=False)
    await message.answer(f"Отправляю обработанный отчёт...", reply_markup=types.ReplyKeyboardRemove())
    flag = False
    start_time = time.time()

    # Ждем 20 сек на создание файла
    while not flag and time.time() - start_time < 20:
        try:
            file = input_file.InputFile(os.path.join(PATH_TO_RESULT_REPORT, f'{message.chat.id}.xlsx'),
                                        filename='result.xlsx')

            await message.answer_document(file)
            flag = True
        except Exception:
            continue

    if flag:
        await message.answer(f"Если хотите построить диаграмму, используйте команду /plot.",
                             reply_markup=types.ReplyKeyboardRemove())
