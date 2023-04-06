from aiogram.filters.callback_data import CallbackData
from typing import Literal, Optional
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


class ScheduleMenuCallbackFactory(CallbackData, prefix="teacher_schedule_menu"):
    type: ScheduleTypes
    id: Optional[int] = None


class ShowScheduleCallbackFactory(CallbackData, prefix="show_teacher_schedule"):
    show: Show
    week_type: InlineWeekTypes = InlineWeekTypes.CURRENT


class ChooseDayCallBackFactory(CallbackData, prefix="choose_day"):
    weekday_index: int | Literal["FULL"]


class ChooseWeekTypeCallbackFactory(CallbackData, prefix="choose_week_type"):
    week_type: InlineWeekTypes


class SelectGroupCallbackFactory(CallbackData, prefix="select_group"):
    selected_group: str


class FullScheduleNavCallbackFactory(CallbackData, prefix="full_schedule_nav"):
    index: int


class ChooseModifyActionCallbackFactory(CallbackData, prefix="choose_modify_action"):
    action: ModifyActions


class ChooseModifyWeekCallbackFactory(CallbackData, prefix="choose_modify_week"):
    week: InlineWeekTypes
