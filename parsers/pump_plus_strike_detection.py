import re


def parse_pumpdetection_plus_strikedetection(comment: str) -> tuple:
    """ Парсит комментарий PumpDetection+StrikeDetection.txt

    :param comment: комментарий
    :return: (заголовки, значения, тип), где 1 - PumpDetection, 2 - остальное
    """

    comment = comment.lstrip()
    headers, values = [], []

    headers.append('Тип стратегии')
    headers.append('Название стратегии')
    headers.append('Пара')

    if comment.startswith('PumpDetection'):
        values.append('PumpDetection')

        comment = comment[comment.find('<'):]

        # Название стратегии
        values.append(comment[comment.find('<'):comment.find('>') + 1])

        pair, comment = comment[comment.find('>') + 2:].split('  ', maxsplit=1)

        # Пара
        values.append(pair)

        # EMA(60sec, 1sec) = -0.04%  Max(30min, 1sec) = -2.44%  BTC(30sec, 1sec) = -0.01%  EMA(15sec, 1sec) = -0.16%  Max(60min, 1sec) = -5.41%  Min(15min, 1sec) = 0.09%  BTC(15sec, 1sec) = -0.01%    CPU: Bot 3 Sys: 39  AppLatency: 0.0 sec  API Req: 57 / 1200   API Orders: 1 / 50   Orders 1D: 1395 / 160000  PriceLag: 0.01% (LUNA PriceLag: 0.01%) Latency: 21 / 21  Ping: 21 / 18
        other_data_zone = comment[comment.find('Dail'):comment.find('EMA')].strip()
        comment = comment[comment.find('EMA'):].lstrip()

        headers.append("DailyVol")
        values.append(other_data_zone[other_data_zone.find(': ') + 1:other_data_zone.find('PPL')].strip())
        other_data_zone = other_data_zone[other_data_zone.find('PPL'):]

        headers.append('PPL/sec')
        values.append(other_data_zone[other_data_zone.find(': ') + 1:other_data_zone.find('Buys/')].strip())
        other_data_zone = other_data_zone[other_data_zone.find('Buys')]

        headers.append('Buys/sec')
        values.append(other_data_zone[other_data_zone.find(': ') + 1:other_data_zone.find('Vol/')].strip())
        other_data_zone = other_data_zone[other_data_zone.find('Vol/')]

        headers.append('Vol/sec')
        values.append(other_data_zone[other_data_zone.find(': '):other_data_zone.find('Price')].strip())
        other_data_zone = other_data_zone[other_data_zone.find('Price')]

        headers.append('PriceDelta')
        values.append(other_data_zone[other_data_zone.find(': ') + 1:other_data_zone.find('EMA')].strip())

        equal_zone, comment = comment.split('    ', maxsplit=1)
        parse_equal = re.findall(r'\w+\(\S+ \S+\) = \S+%', equal_zone)
        for item in parse_equal:
            tmp = item.split(' = ')
            headers.append(tmp[0])
            values.append(tmp[1])

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

        return values, headers, 1
    else:
        if comment.startswith('Joined Sell'):
            values.append('Joined Sell')
            values.append(comment[comment.find(';') + 2:comment.find('EMA')].rstrip())
        elif comment.startswith('MoonStrike'):
            values.append('MoonStrike')
            values.append(comment[comment.find('('):comment.find(')')])
        elif comment.startswith('MoonShot'):
            values.append('MoonShot')
            values.append(comment[comment.find('('):comment.find(')')])

        # Пара
        values.append('')

        # Зона со знаками =
        equal_zone = comment[:comment.find('CPU')].rstrip()
        parse_equal = re.findall(r'\w+\(\S+ \S+\) = \S+%', equal_zone)
        for item in parse_equal:
            tmp = item.split(' = ')
            headers.append(tmp[0])
            values.append(tmp[1])

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
        return values, headers, 2
