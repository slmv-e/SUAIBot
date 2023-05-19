from enum import Enum

from motor.motor_asyncio import AsyncIOMotorCollection
from database import Schedule, Users


async def insert_new_user(tg_id: int, collection: AsyncIOMotorCollection) -> None:
    user_dict = {"tg_id": tg_id, "group": None, "custom_schedule": []}
    if not await collection.find_one(user_dict):
        await collection.insert_one(user_dict)


async def change_user_group(tg_id: int, group: Schedule.Group, collection: AsyncIOMotorCollection) -> None:
    result = await collection.update_one({'tg_id': tg_id}, {'$set': {'group': group}})
    if not result.matched_count:
        await collection.insert_one({'tg_id': tg_id, 'group': group})


async def get_user_custom_schedule(tg_id: int, collection: AsyncIOMotorCollection) -> Schedule.Model | None:
    result = await collection.find_one({'tg_id': tg_id})

    user: Users.Model = Users.Model.parse_obj(result)
    if not user.custom_schedule:
        return None

    for custom_schedule in user.custom_schedule:
        if custom_schedule.group == user.group:
            return custom_schedule

    return None


async def add_custom_schedule(tg_id: int, custom_schedule: Schedule.Model, collection: AsyncIOMotorCollection) -> None:
    user: Users.Model = Users.Model.parse_obj(await collection.find_one({'tg_id': tg_id}))
    custom_schedule.week = list(filter(lambda day: day.pairs, custom_schedule.week))

    def serializer(schedule):
        # родитель, ключ, значение
        stack = [[None, None, schedule]]

        while stack:
            parent, parent_key, item = stack.pop()

            if isinstance(item, dict):
                for key, value in item.items():
                    stack.append([item, key, value])
            elif isinstance(item, list):
                for ind, value in enumerate(item):
                    stack.append([item, ind, value])
            elif isinstance(item, Enum):
                parent[parent_key] = item.value

        return schedule

    for index, user_custom_schedule in enumerate(user.custom_schedule):
        if user_custom_schedule.group == custom_schedule.group:
            user.custom_schedule[index] = custom_schedule
            break
    else:
        user.custom_schedule.append(custom_schedule)

    custom_schedule_array = [
        serializer(user_custom_schedule.dict())
        for user_custom_schedule in user.custom_schedule
    ]

    await collection.update_one(
        {'tg_id': tg_id},
        {'$set': {'custom_schedule': custom_schedule_array}}
    )


async def get_user_group(tg_id: int, collection: AsyncIOMotorCollection) -> Schedule.Group | None:
    user_dict = {"tg_id": tg_id}
    if user := await collection.find_one(user_dict):
        return Users.Model(**user).group
    return None

