import re


def parse_moonHook_plus_spreaddetection_comment(comment: str) -> tuple:
    """ Парсит комментарий MoonHook+SpreadDetection.txt

    :param comment: строка комментария
    :return: (значения, заголовки)
    """

    headers, values = [], []

    headers.append('Тип стратегии')
    strategy_type = comment[:comment.find('CPU') - 1].rstrip()

    if strategy_type.find('Hook Long Depth') == -1:
        flag = False
        values.append(comment[:comment.find('CPU') - 1].rstrip())
    else:
        flag = True
        values.append(comment[comment.find('<') + 1:comment.find('>')])
        additional_info = comment[:comment.find('CPU')]

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
    headers.append('Orders 1D')
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

    if flag:
        headers.append('Hook Long Depth')
        values.append(additional_info[additional_info.find(': ')+1:additional_info.find('R')].strip())
        additional_info = additional_info[additional_info.find('R'):]

        headers.append('R')
        values.append(additional_info[additional_info.find(': ')+1:additional_info.find('d')].strip())
        additional_info = additional_info[additional_info.find('d'):]

        headers.append('d')
        values.append(additional_info[additional_info.find(': ')+1:additional_info.find('(')].strip())
        additional_info = additional_info[additional_info.find('High'):]

        headers.append('High')
        values.append(additional_info[additional_info.find(': ')+1:additional_info.find('Min')].strip())
        additional_info = additional_info[additional_info.find('Min'):]

        headers.append('Min')
        values.append(additional_info[additional_info.find(': ')+1:additional_info.find('Max')].strip())
        additional_info = additional_info[additional_info.find('Max'):]

        headers.append('Max')
        values.append(additional_info[additional_info.find(': ')+1:additional_info.find('[')].strip())
        additional_info = additional_info[additional_info.find('AbsHigh'):]

        headers.append('AbsHigh')
        values.append(additional_info[additional_info.find(': ')+1:additional_info.find('Drop')].strip())
        additional_info = additional_info[additional_info.find('Drop'):]

        headers.append('Drop')
        values.append(additional_info[additional_info.find(': ')+1:additional_info.find(']')].strip())
        additional_info = additional_info[additional_info.find('VolK'):]

        headers.append('VolK')
        values.append(additional_info[additional_info.find(': ')+1:additional_info.find(')')].strip())
        additional_info = additional_info[additional_info.find('Initial'):]

        headers.append('InitialPrice')
        values.append(additional_info[additional_info.find(': ')+1:additional_info.find('Buffer')].strip())
        additional_info = additional_info[additional_info.find('Buffer'):]

        headers.append('Buffer')
        values.append(additional_info[additional_info.find('[')+1:additional_info.find(']')].strip())
        additional_info = additional_info[additional_info.find('Sell'):]

        headers.append('SellPrice')
        values.append(additional_info[additional_info.find(': ')+1:additional_info.find('EMA')].strip())

    return values, headers


def parse_hook_long_depth_comment(comment: str) -> tuple:
    """ Парсит комментарий hook_long_depth

    :param comment: Комментария для обработки
    :return: (values, headers)
    """

    headers, values = [], []
    headers.append('Тип стратегии')
    values.append('Hook Long Depth')

    if comment.find('EMA') != -1:
        index_CPU = comment.find('CPU')
        equal_zone = comment[comment.find('EMA'):index_CPU].strip()
        comment = comment[comment.find('R'):comment.find('EMA')] + comment[index_CPU:]
        parse_equal = re.findall(r'\w+\(\S+ \S+\) = \S+%', equal_zone)
        for item in parse_equal:
            tmp = item.split(' = ')
            headers.append(tmp[0])
            values.append(tmp[1])
    else:
        comment = comment[comment.find('R'):]

    d_index = comment.find('d')
    headers.append('R')
    values.append(comment[comment.find('R:') + 2:d_index].strip())

    high_index = comment.find('(High')
    headers.append('d')
    values.append(comment[d_index + 2:high_index].strip())

    min_index = comment.find('Min')
    headers.append('High')
    values.append(comment[high_index + 6:min_index].strip())

    max_index = comment.find('Max')
    headers.append('Min')
    values.append(comment[min_index + 4:max_index].strip())

    abshigh_index = comment.find('AbsHigh')
    headers.append('Max')
    values.append(comment[max_index + 4:abshigh_index - 1].strip())

    drop_index = comment.find('Drop')
    headers.append('AbsHigh')
    values.append(comment[abshigh_index + 8:drop_index].strip())

    volk_index = comment.find('VolK')
    headers.append('Drop')
    values.append(comment[drop_index + 5:volk_index].strip())

    initial_price_index = comment.find('InitialPrice')
    headers.append('VolK')
    values.append(comment[volk_index + 5:initial_price_index].strip())

    buffer_index = comment.find('Buffer')
    headers.append('InitialPrice')
    values.append(comment[initial_price_index + 13:buffer_index].strip())

    sell_price_index = comment.find('SellPrice')
    headers.append('Buffer')
    values.append(comment[buffer_index + 9:sell_price_index - 2])

    cpu_index = comment.find('CPU')
    headers.append('SellPrice')
    values.append(comment[sell_price_index + 10:cpu_index].strip())

    comment = comment[cpu_index:]

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
    headers.append('Orders 1D')
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
    return values, headers


def parse_moonstrike_comment(comment: str) -> tuple:
    """Парсит комментарий MoonStrike.

    :param comment: Комментарий для парсинга
    :return: (values, headers)
    """

    headers, values = [], []

    headers.append('Тип стратегии')
    values.append('MoonStrike')
    headers.append('Название стратегии')
    values.append(comment[comment.find('<'):comment.find('>')+1])

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

    headers.append('CPU')
    values.append(comment[comment.find('CPU') + 4:comment.find('Sys')].strip())
    comment = comment[comment.find('Sys'):]

    headers.append('Sys')
    values.append(comment[comment.find('Sys') + 4:comment.find('App')].strip())
    comment = comment[comment.find('App'):]

    headers.append('AppLatency')
    values.append(comment[comment.find(':') + 1:comment.find('API')].strip())
    comment = comment[comment.find('API'):]

    headers.append('API Req')
    values.append(comment[comment.find(':') + 1:comment.find('API Ord')].strip())
    comment = comment[comment.find('API Ord'):]

    headers.append('API Orders')
    if comment[5:].find('Orders') != -1:
        values.append(comment[comment.find(':') + 1:comment[5:].find('Orders')].strip())
        comment = comment[comment[5:].find('Orders'):]

        headers.append(comment[:comment.find(':')].strip())
        values.append(comment[comment.find(':') + 1:comment.find('Price')].strip())
        comment = comment[comment.find('Price'):]
    else:
        values.append(comment[comment.find(':') + 1:comment.find('Price')].strip())
        comment = comment[comment.find('Price'):]

    headers.append('PriceLag')
    values.append(comment[comment.find(':') + 1:comment.find('(')].strip())
    comment = comment[comment.find('('):]

    headers.append('Вид PriceLag')
    values.append(comment[1:comment.find(')')].strip())
    comment = comment[comment.find('Lat'):]

    headers.append('Latency')
    values.append(comment[comment.find(':') + 1:comment.find('Ping')].strip())
    comment = comment[comment.find('Ping'):]

    headers.append('Ping')
    values.append(comment[comment.find(':') + 1:].strip())

    return values, headers
