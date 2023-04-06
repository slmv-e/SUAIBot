from motor.motor_asyncio import AsyncIOMotorCollection
from database import Teachers


async def get_all(collection: AsyncIOMotorCollection):
    teachers_raw = await collection.find().to_list(length=None)
    return [Teachers.Model(**teacher_raw) for teacher_raw in teachers_raw]
