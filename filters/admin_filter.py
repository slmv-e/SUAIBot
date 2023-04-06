from aiogram.filters import BaseFilter
from aiogram.types import Message


class AdminFilter(BaseFilter):
    def __init__(self, ids: list[int]):
        self.admin_ids = ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids
