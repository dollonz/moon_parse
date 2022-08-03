from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from typing import Union

from config import ADMINS


class AdminFilter(BoundFilter):
    key = "is_admin"

    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def check(self, message: Union[types.Message, types.CallbackQuery]) -> bool:
        """Проверка id пользователя на админа.

        :param message: Телеграмм сообщение.
        :return: True если пользователь - админ.
        """

        if type(message) == types.CallbackQuery:
            return message.message.chat.id
        else:
            return message.chat.id in ADMINS
