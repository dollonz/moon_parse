import logging
import re


def parse_DropsDetection_comment(comment: str) -> tuple:
    """ Парсит комментарий DropsDetction.txt

    :param comment: строка комментария
    :return: (values, headers)
    """
    res = {}

    try:
        res['Тип стратегии'] = comment.split(':', maxsplit=1)[0].strip()
    except AttributeError:
        logging.error(f"Error in parse_DropsDetection_comment function. Can not find Тип стратегии.")

    try:
        res['Название стратегии'] = re.search(r'\s<.+>\s', comment).group(0).strip()
    except AttributeError:
        logging.error(f"Error in parse_DropsDetection_comment function. Can not find Название стратегии.")

    try:
        res['Пара'] = re.search(r'\s\w+-\w+\s', comment).group(0).strip()
    except AttributeError:
        logging.error(f"Error in parse_DropsDetection_comment function. Can not find Пара.")

    # Очистка того, что распарсили
    comment = comment[comment.find('Daily'):]
    comment = comment.split(': ', maxsplit=3)

    # DailyVol, PriceIsLow, xPriceDelta
    res[comment[0]] = comment[1].split(' ', maxsplit=1)[0]
    res[comment[1].split(' ', maxsplit=1)[1]] = comment[2].split(' ', maxsplit=1)[0]
    res[comment[2].split(' ', maxsplit=1)[1]] = comment[3].split(' ', maxsplit=1)[0]

    # Очистка того, что распарсили
    comment = comment[3].split(' ', maxsplit=1)[1]

    # Зона со знаками =
    equal_area, comment = comment.split('    ', maxsplit=1)
    parse_equal = re.findall(r'\w+\(\S+ \S+\) = \S+%', equal_area)
    for elem in parse_equal:
        tmp = elem.split(' = ', maxsplit=1)
        res[tmp[0]] = tmp[1]

    # CPU, AppLatency, API Req, API Orders, PriceLag, PriceLag, Latency, Ping
    tmp = comment.split(': ', maxsplit=6)
    Sys_index = tmp[1].find('Sys')
    res['CPU'] = tmp[1][:Sys_index].strip()
    AppLatency_index = tmp[2].find('AppL')
    res['Sys'] = tmp[2][:AppLatency_index].strip()
    API_Req_index = tmp[3].find('API R')
    res['AppLatency'] = tmp[3][:API_Req_index].strip()
    API_Orders = tmp[4].find('API Orders')
    res['API Req'] = tmp[4][:API_Orders].strip()
    PriceLag_index = tmp[5].find('PriceLag')
    res['API Orders'] = tmp[5][:PriceLag_index].strip()
    Other_data_index = tmp[6].find('(')
    res['PriceLag'] = tmp[6][:Other_data_index]

    comment = tmp[-1].split(' ', maxsplit=1)[1]

    res['Вид PriceLag'] = comment[:comment.find(')') + 1]

    comment = comment[comment.find(')') + 1:].lstrip()

    tmp = comment.split(': ')

    res['Latency'] = ' '.join(tmp[1].split(' ')[:-1])
    res['Ping'] = tmp[-1]

    return list(res.values()), list(res.keys())
