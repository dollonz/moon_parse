def parse_PuvpDetection(comment: str) -> tuple:
    """ Парсит комментарий PuvpDetection.txt

    :param comment: комментарий
    :return: (значения, заголовки)
    """
    comment = comment.lstrip()
    headers, values = [], []

    headers.append('Тип стратегии')
    headers.append('Название стратегии')
    headers.append('Пара')

    values.append('PumpDetection')

    comment = comment[comment.find('<'):]

    # Название стратегии
    values.append(comment[comment.find('<'):comment.find('>') + 1])

    pair, comment = comment[comment.find('>') + 2:].split('  ', maxsplit=1)

    # Пара
    values.append(pair)

    other_data_zone = comment[comment.find('Dail'):comment.find('CPU')].strip()

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
    values.append(other_data_zone[other_data_zone.find(': ') + 1:other_data_zone.find('CPU')].strip())

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

    return values, headers
