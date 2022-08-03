import string
import random

characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
PASSWORD_LEN = 24


def generate_random_password():
    """Функция, генерирующая рандомные пароли длиной PASSWORD_LEN символов.

    :return: Пароль
    """
    random.shuffle(characters)

    password = []
    for i in range(PASSWORD_LEN):
        password.append(random.choice(characters))

    random.shuffle(password)

    return "".join(password)
