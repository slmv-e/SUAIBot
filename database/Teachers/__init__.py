from pydantic import BaseModel
from database.Schedule import BaseSchedule
from typing import TypeVar
from database.Teachers import handlers

Email = TypeVar("Email", bound=str | None)
PhoneNumber = TypeVar("PhoneNumber", bound=str | None)
Audience = TypeVar("Audience", bound=str | None)


class TeacherID(int):
    pass


class Position(BaseModel):
    job_title: str
    short_name: str
    full_name: str


class Contacts(BaseModel):
    email: Email
    audience: Audience
    phone: PhoneNumber


class Model(BaseModel):
    id: TeacherID
    name: str
    photo_url: str
    job_title: str | None
    contacts: Contacts | None
    positions: list[Position]
    full_info_url: str
    schedule: BaseSchedule | None
