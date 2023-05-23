from aiogram.filters.callback_data import CallbackData
from typing import Literal, Optional
from routes.users.misc.types.enum import ScheduleTypes, Show, InlineWeekTypes, ModifyActions, Buidings
from routes.users.utils.types import PairTypes


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


class ChooseModifyPairCallbackFactory(CallbackData, prefix="choose_modify_pair"):
    day_index: int
    number: int | str
    week: InlineWeekTypes


class ChoosePairTypeCallbackFactory(CallbackData, prefix="choose_pair_type"):
    pair_type: PairTypes


class ChooseBuildingCallbackFactory(CallbackData, prefix="choose_building"):
    building: Buidings
