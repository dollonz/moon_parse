import re


def parse_StreadDetection(comment: str) -> tuple:
    """ Парсит комментарий PuvpDetection.txt

    :param comment: комментарий
    :return: (значения, заголовки)
    """
    headers, values = [], []

    headers.append('Тип стратегии')
    values.append('SpreadDetection')
    headers.append('Название стратегии')
    values.append(comment[comment.find('<'):comment.find('>')+1])

    if comment.find('EMA') != -1:
        index_CPU = comment.find('CPU')
        index_EMA = comment.find('EMA')
        equal_zone = comment[index_EMA:index_CPU].strip()
        comment = comment[:index_EMA] + comment[index_CPU:]
        if comment[:comment.find('CPU')].find('(') != -1:
            comment = comment[:comment.find('(')] + comment[comment.find('>)') + 2:]
            if comment.find('Rpt') != -1:
                comment = comment[:comment.find('(')] + comment[comment.find('>)') + 2:]
        parse_equal = re.findall(r'\w+\(\S+ \S+\) = \S+%', equal_zone)
        for item in parse_equal:
            tmp = item.split(' = ')
            headers.append(tmp[0])
            values.append(tmp[1])

    comment = comment[comment.find('TD'):]

    headers.append('TD')
    values.append(comment[comment.find(': ') + 1:comment.find('TD2')].strip())
    comment = comment[comment.find('TD2'):]

    headers.append('TD2')
    values.append(comment[comment.find(': ') + 1:comment.find('dP')].strip())
    comment = comment[comment.find('dP'):]

    headers.append('dP')
    values.append(comment[comment.find(': ') + 1:comment.find('Vol')].strip())
    comment = comment[comment.find('Vol'):]

    headers.append('Vol')
    values.append(comment[comment.find(': ') + 1:comment.find('Trades')].strip())
    comment = comment[comment.find('Trades'):]

    headers.append('Trades')
    values.append(comment[comment.find(': ') + 1:comment.find('Spread')].strip())
    comment = comment[comment.find('Spread'):]

    headers.append('Spread')
    values.append(comment[comment.find(': ') + 1:comment.find('N')].strip())
    comment = comment[comment.find('N'):]

    headers.append('N')

    if comment.find('bv/sv') != -1:
        values.append(comment[comment.find(': ') + 1:comment.find('bv/sv')].strip())
        comment = comment[comment.find('bv/sv'):]

        headers.append('bv/sv')
        values.append(comment[comment.find(': ') + 1:comment.find('CPU')].strip())
    else:
        values.append(comment[comment.find(': ') + 1:comment.find('CPU')].strip())

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
