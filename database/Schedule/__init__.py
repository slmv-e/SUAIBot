import datetime
from typing import Literal, NamedTuple
from enum import Enum
from pydantic import BaseModel
from database.Schedule import handlers


class Group(str):
    pass


class PairTime(NamedTuple):
    start: datetime.time
    end: datetime.time


class PairsTime(tuple):
    def __new__(cls):
        pairs_time = (
            PairTime(
                start=datetime.time(9, 30),
                end=datetime.time(11, 00)
            ),
            PairTime(
                start=datetime.time(11, 10),
                end=datetime.time(12, 40)
            ),
            PairTime(
                start=datetime.time(13, 0),
                end=datetime.time(14, 30)
            ),
            PairTime(
                start=datetime.time(15, 0),
                end=datetime.time(16, 30)
            ),
            PairTime(
                start=datetime.time(16, 40),
                end=datetime.time(18, 10)
            ),
            PairTime(
                start=datetime.time(18, 30),
                end=datetime.time(20, 0)
            ),
            PairTime(
                start=datetime.time(20, 10),
                end=datetime.time(21, 40)
            ),
        )
        return super().__new__(cls, pairs_time)

    def at(self, pair_number) -> PairTime:
        if not isinstance(pair_number, int):
            raise TypeError("Only int support")
        if 1 <= pair_number <= 7:
            return super().__getitem__(pair_number - 1)
        else:
            raise KeyError("Pair doesn't exists")


class PairDetails(BaseModel):
    name: str
    type: Literal["ПР", "ЛР", "Л", "КР", "КП"]
    audience: str
    groups: list[str]
    teacher_names: list[str]


class WeekBaseUpper(Enum):
    arrow = "▲"
    circle = "🔴"


class WeekBaseLower(Enum):
    arrow = "▼"
    circle = "🔵"


class WeekDifferentPairs(BaseModel):
    upper: PairDetails | None
    lower: PairDetails | None


class Pair(BaseModel):
    number: int | Literal["вне сетки расписания"]
    details: PairDetails | WeekDifferentPairs


class DayName(Enum):
    SCHEDULE_GRID_OUT = "Вне сетки расписания"
    MONDAY = "Понедельник"
    TUESDAY = "Вторник"
    WEDNESDAY = "Среда"
    THURSDAY = "Четверг"
    FRIDAY = "Пятница"
    SATURDAY = "Суббота"
    SUNDAY = "Воскресенье"


class Day(BaseModel):
    name: DayName
    weekday_index: int
    pairs: list[Pair]


class BaseSchedule(BaseModel):
    week: list[Day]


class Model(BaseSchedule):
    group: str
