from motor.motor_asyncio import AsyncIOMotorCollection
from database import Schedule, Users


async def insert_new_user(tg_id: int, collection: AsyncIOMotorCollection) -> None:
    user_dict = {"tg_id": tg_id}
    if not await collection.find_one(user_dict):
        await collection.insert_one(user_dict)


async def change_user_group(tg_id: int, group: Schedule.Group, collection: AsyncIOMotorCollection) -> None:
    result = await collection.update_one({'tg_id': tg_id}, {'$set': {'group': group}})
    if not result.matched_count:
        await collection.insert_one({'tg_id': tg_id, 'group': group})


async def get_user_group(tg_id: int, collection: AsyncIOMotorCollection) -> Schedule.Group | None:
    user_dict = {"tg_id": tg_id}
    if user := await collection.find_one(user_dict):
        return Users.Model(**user).group
    return None

