import re


def parse_EMA_comment(comment: str) -> tuple:
    """ Парсит комментарий EMA.txt

    Название стратегии находится не в поле comment.

    :param comment: строка комментария
    :return: (значения, заголовки )
    """

    headers = []
    values = []

    headers.append('Тип стратегии')
    values.append(comment.split(': ', maxsplit=1)[0])

    if comment.find('EMA') != -1:
        index_CPU = comment.find('CPU')
        equal_zone = comment[:index_CPU].strip()
        comment = comment[index_CPU:]
        parse_equal = re.findall(r'\w+\(\S+ \S+\) = \S+%', equal_zone)
        for item in parse_equal:
            tmp = item.split(' = ')
            headers.append(tmp[0])
            values.append(tmp[1])
    else:
        comment = comment[comment.find('CPU'):]

    tmp = comment.split(': ', maxsplit=7)

    Sys_index = tmp[1].find('Sys')
    headers.append('CPU')
    values.append(tmp[1][:Sys_index].strip())

    AppLatency_index = tmp[2].find('AppL')
    headers.append('Sys')
    values.append(tmp[2][:AppLatency_index].strip())

    API_Req_index = tmp[3].find('API R')
    headers.append('AppLatency')
    values.append(tmp[3][:API_Req_index].strip())

    API_Orders = tmp[4].find('API Orders')
    headers.append('API Req')
    values.append(tmp[4][:API_Orders].strip())

    Orders_index = tmp[5].find('Orders')
    headers.append('API Orders')
    values.append(tmp[5][:Orders_index].strip())

    PriceLag_index = tmp[6].find('PriceLag')
    headers.append('Orders 10S')
    values.append(tmp[6][:PriceLag_index].strip())

    Other_data_index = tmp[7].find('(')
    headers.append('PriceLag')
    values.append(tmp[7][:Other_data_index].strip())

    comment = tmp[-1].split(' ', maxsplit=1)[1]

    headers.append('Вид PriceLag')
    values.append(comment[:comment.find(')') + 1])

    comment = comment[comment.find(')') + 1:].lstrip()

    tmp = comment.split(': ')

    headers.append('Latency')
    values.append(' '.join(tmp[1].split(' ')[:-1]))
    headers.append('Ping')
    values.append(tmp[-1])
    print(values, headers)
    return values, headers
