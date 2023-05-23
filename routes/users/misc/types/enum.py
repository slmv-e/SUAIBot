from enum import Enum


class Show(Enum):
    TODAY = "today"
    TOMORROW = "tomorrow"
    WEEK = "week"


class InlineWeekTypes(Enum):
    CURRENT = "current"
    FULL = "full"
    UPPER = "upper"
    LOWER = "lower"


class ScheduleTypes(Enum):
    TEACHER = "teacher"
    GROUP = "group"


class ScheduleButtons(Enum):
    MONDAY = "Пн"
    TUESDAY = "Вт"
    WEDNESDAY = "Ср"
    THURSDAY = "Чт"
    FRIDAY = "Пт"
    SATURDAY = "Сб"
    FULL = "Вся неделя"


class ModifyActions(Enum):
    ADD = "add"
    REMOVE = "remove"
    TRANSFER = "transfer"


class Buidings(Enum):
    BOLSHAYA_MORSKAYA = "Б. Морская 67"
    GASTELLO = "Гастелло 15"
    LENSOVETA = "Ленсовета 14"
