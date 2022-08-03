import psycopg2
import os
import logging

from aiogram import types
from configparser import ConfigParser

from config import PATH_TO_DATABASE_INI


class DBManager:
    """Менеджер управления базой данных. Вся работа с БД происходит именно через этот класс.

    Attributes
    ----------
    ...

    Methods
    -------
    ...
    """

    __instance = None
    connection = None
    db = None

    def __init__(self):
        """Конструктор класса, реализующий паттерн проектирования - одиночка."""

        if DBManager.__instance is not None:
            logging.info(f"DBManager singleton is already created.")
            return

        logging.info(f"Construct DBManager singleton.")

        self.db = self.download_config()
        logging.info(f"Successfully parsed database.ini file. Attempting connect to database.")

        try:
            self.connection = psycopg2.connect(**self.db)
            logging.info(f"Successfully connected to database.")
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(f"Failed to construct DBManager singleton.\n{error}")

    @classmethod
    def get_instance(cls) -> __instance:
        """Вызывает конструктор класса, если сущность не была создана.

        :return: __instance
        """
        if not cls.__instance:
            logging.info(f"Calling DBManager constructor in get_instance method.")
            cls.__instance = DBManager()
        logging.info(f"Returning instance of DBManager class.")
        return cls.__instance

    def __del__(self):
        """Деструктор класса.

        Закрывает соединение с базой данных, если оно было открыто.

        :return: None
        """

        logging.info(f"Destructor of DBManager class called.")
        if self.connection is not None:
            logging.info(f"Closing connection to database.")
            self.connection.close()

    @staticmethod
    def download_config(file_name: str = PATH_TO_DATABASE_INI, section: str = 'postgresql') -> dict:
        """Создание файла конфига для подключения к БД.

        В файле database.ini обязательно должны присутствовать следующие поля
        (в скобках указаны параметры по умолчанию):
        - host (=localhost)
        - database (=access_codes)
        - user (=postgres)
        - password (=123qweasd)

        :param section: Секция для парсинга в файле конфига.
        :param file_name: Путь к файлу конфига.

        :return: Словарь конфига
        """

        if not os.path.exists(PATH_TO_DATABASE_INI):
            msg = "Database.ini file not exist. Please make it to use DB"
            logging.error(msg)
            raise FileNotFoundError(msg)

        parser = ConfigParser()
        parser.read(file_name)
        db = {}

        if parser.has_section(section):
            params = parser.items(section)
            for key, value in params:
                db[key] = value
        else:
            raise Exception(f"Section {section} not found in {file_name}.")

        return db

    def create_table(self):
        """Первичное создание таблиц.

        :return: None
        """
        commands = (
            """
            CREATE TABLE IF NOT EXISTS tg_user (
                id BIGSERIAL PRIMARY KEY NOT NULL,
                username VARCHAR(150) NOT NULL UNIQUE,
                tg_id INT NOT NULL UNIQUE,
                has_access BOOLEAN NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS codes (
                id BIGSERIAL PRIMARY KEY NOT NULL,
                user_tg_id INT,
                code VARCHAR(24) NOT NULL UNIQUE,
                CONSTRAINT fk_tg_user
                    FOREIGN KEY (user_tg_id)
                        REFERENCES tg_user(tg_id)
                            ON DELETE SET NULL
            );
            """
        )

        logging.info(f"Creating tables in database.")

        try:
            cursor = self.connection.cursor()
            for cmd in commands:
                cursor.execute(cmd)
                self.connection.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(error)

    def check_if_code_is_occupied(self, code: str) -> bool:
        """Проверяет занят ли заданный код кем-либо.

        :param code: код для проверки.
        :return: True, если код занят.
        """

        query = f"""SELECT user_tg_id FROM codes WHERE code='{code}'"""
        cursor = self.connection.cursor()
        cursor.execute(query)
        occupied = cursor.fetchone() is not None
        cursor.close()
        return occupied

    def get_username_by_code(self, code: str) -> str:
        """Возвращает имя пользователя по заданному коду.

        Во избежание ошибок код должен существовать и принадлежать кому-то.
        Для проверки принадлежности кода используйте функцию check_if_code_is_occupied.

        :param code: Код доступа.
        :return: Имя пользоваетля.
        """

        query = f"""SELECT user_tg_id FROM codes WHERE code='{code}';"""
        cursor = self.connection.cursor()
        cursor.execute(query)
        tg_id = cursor.fetchone()[0]

        query = f"""SELECT username FROM tg_user WHERE tg_id={tg_id} LIMIT 1;"""
        cursor.execute(query)
        username = cursor.fetchone()[0]
        cursor.close()

        return username

    def get_access_code_by_username(self, username: str) -> str:
        """Возвращает код доступа у заданного пользователя.

        Во избежание ошибок пользователь должен иметь доступ к боту!
        Для проверки используйте функцию check_access_by_username или check_if_user_has_access.

        :param username: Имя пользователя тг.
        :return: Код доступа.
        """

        query = f"""SELECT tg_id FROM tg_user WHERE username='{username}' LIMIT 1;"""
        cursor = self.connection.cursor()
        cursor.execute(query)
        tg_id = cursor.fetchone()[0]

        query = f"""SELECT code FROM codes WHERE user_tg_id={tg_id} LIMIT 1;"""
        cursor.execute(query)
        code = cursor.fetchone()[0]
        cursor.close()

        return code

    def check_access_by_username(self, username: str) -> bool:
        """Проверяет доступ к БД у пользователя с заданным username.

        :param username: Имя пользователя на серверах тг.
        :return: True, если доступ есть.
        """
        logging.info(f"Checking access by username")
        query = f"""SELECT has_access FROM tg_user WHERE username='{username}' LIMIT 1;"""
        cursor = self.connection.cursor()
        cursor.execute(query)
        access = cursor.fetchone()[0]
        cursor.close()
        logging.info(f"{username} has no access." if not access else f"{username} has access.")
        return access

    def check_if_user_exist(self, username: str, tg_id: int) -> bool:
        """Проверяет есть ли пользователь с username и tg_id в БД.

        Также проверяет случай, когда пользователь менял username в тг, но уже был в таблице.

        :param username - Имя пользователя в телеграмм.
        :param tg_id - ID пользователя на серверах телеграмм.

        :return: True если пользователь есть, иначе - False.
        """

        query = f"""SELECT id FROM tg_user WHERE username='{username}' AND tg_id={tg_id} LIMIT 1;"""
        cursor = self.connection.cursor()
        cursor.execute(query)
        exist = cursor.fetchone() is not None

        if exist is not None:
            query = f"""SELECT id FROM tg_user WHERE tg_id={tg_id} LIMIT 1;"""
            cursor.execute(query)
            id_exist = cursor.fetchone()
            if id_exist is not None:
                logging.info(f"User {username} recently changed his username. Updating database.")
                query = f"""UPDATE tg_user SET username='{username}' WHERE tg_id={tg_id};"""
                cursor.execute(query)
                self.connection.commit()
                exist = True

        cursor.close()
        return exist

    def create_user(self, message: types.Message) -> None:
        """Записывает пользователя в БД.

        :return: None
        """
        logging.info(f"Creating user {message.chat.username} into database.")

        username = message.chat.username
        tg_id = message.chat.id

        if not self.check_if_user_exist(username, tg_id):
            cursor = self.connection.cursor()
            query = f"""INSERT INTO tg_user (username, tg_id, has_access) 
                                    VALUES ('{username}', {tg_id}, false);"""
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
            logging.info(f"User {username} inserted into database.")

    def check_if_user_has_access(self, username: str, tg_id: int) -> bool:
        """Проверяет доступ к боту для пользователя.

        :param username: Имя пользователя телеграмм.
        :param tg_id: Телеграмм id.
        :return: True если доступ разрешен.
        """
        logging.info(f"Checking if user {username} has access to bot.")
        query = f"""SELECT has_access FROM tg_user WHERE username='{username}' AND 
                    tg_id={tg_id} LIMIT 1;"""
        cursor = self.connection.cursor()
        cursor.execute(query)
        try:
            access = cursor.fetchone()[0]
        except TypeError:
            cursor.close()
            return False
        cursor.close()
        return access

    def execute_custom_query(self, query: str) -> None:
        """Выполняет запрос к БД.

        Пока что используется только для создания кодов доступа!!!

        :param query: Запрос к БД.
        :return: None
        """
        logging.info(f"Executing query.")

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(error)

    def check_access_code(self, message: types.Message, code: str) -> tuple:
        """Проверяет код, отправленный пользователем, на корректность.

        Если код занят, то сообщает об этом.
        Если код свободен, то присваивает его к пользователю и выдаёт доступ.

        :param message: Сообщение от пользователя, в котором хранится код.
        :param code: Собственно, сам код.
        :return: кортеж:
            (Сообщение, которое должно быть отправлено пользователю, (True если успех, иначе - Flalse))
        """
        logging.info(f"Trying to give permission to {message.chat.username}")

        query = f"""SELECT id, user_tg_id FROM codes WHERE code='{code}';"""
        cursor = self.connection.cursor()
        cursor.execute(query)

        answer = cursor.fetchone()

        if answer is None:
            logging.info(f"Incorrect code.")
            text, ans = f"Код введён неверно. Повторите попытку", False
        elif answer[1] is None:
            logging.info(f"Correct code. Giving permission to {message.chat.username}")

            query = f"""UPDATE codes SET user_tg_id={message.chat.id} WHERE code='{code}';"""
            cursor.execute(query)

            query = f"""UPDATE tg_user SET has_access=true WHERE 
            username='{message.chat.username}' AND tg_id={message.chat.id};"""
            cursor.execute(query)

            self.connection.commit()

            text, ans = "Вам выдан доступ к боту.\n\nДля быстрого старта используйте команду /parse", \
                        True
        else:
            logging.info(f"This code is already used by {answer[1]}")
            text, ans = ("Этот код уже используется другим пользователем, "
                         "пожалуйста, повторите попытку.", False)

        cursor.close()
        return text, ans

    def remove_access_by_username(self, username: str) -> None:
        """Забрать доступ к боту у пользователя с заданным username.

        :param username: Имя пользователя.
        :return: None
        """

        logging.info(f"Removing {username} access to bot.")
        query = f"""UPDATE tg_user SET has_access=false WHERE username='{username}';"""
        cursor = self.connection.cursor()
        cursor.execute(query)

        query = f"""SELECT tg_id FROM tg_user WHERE username='{username}';"""
        cursor.execute(query)
        tg_id = cursor.fetchone()[0]

        query = f"""SELECT code FROM codes WHERE user_tg_id={tg_id} LIMIT 1;"""
        cursor.execute(query)
        code = cursor.fetchone()[0]

        query = f"""UPDATE codes SET user_tg_id=NULL WHERE code='{code}';"""
        cursor.execute(query)
        self.connection.commit()
        cursor.close()
