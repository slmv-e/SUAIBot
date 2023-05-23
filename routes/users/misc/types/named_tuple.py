from typing import NamedTuple

from database.Schedule import WeekBaseLower, WeekBaseUpper


class PairNumbers(NamedTuple):
    number: int
    week: WeekBaseLower | WeekBaseUpper | None = None