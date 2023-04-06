from pydantic import BaseModel
from database import Schedule
from database.Users import handlers


class Model(BaseModel):
    tg_id: int
    group: Schedule.Group | None
    custom_schedule: list[Schedule.Model] | None
