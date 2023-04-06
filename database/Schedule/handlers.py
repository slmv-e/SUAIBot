from motor.motor_asyncio import AsyncIOMotorCollection
from database import Schedule


async def get_all(collection: AsyncIOMotorCollection):
    groups_schedule_raw = await collection.find().to_list(length=None)
    return [Schedule.Model(**group) for group in groups_schedule_raw]
