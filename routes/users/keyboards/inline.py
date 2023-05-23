from typing import Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from database import Teachers
from database.Schedule import WeekBaseUpper, WeekBaseLower
from routes.users.callback_factories import ChooseModifyActionCallbackFactory, \
    ChooseBuildingCallbackFactory, ChooseModifyPairCallbackFactory, ChooseModifyWeekCallbackFactory, \
    ChoosePairTypeCallbackFactory, ChooseWeekTypeCallbackFactory, ScheduleMenuCallbackFactory, \
    ShowScheduleCallbackFactory, ChooseDayCallBackFactory, SelectGroupCallbackFactory, FullScheduleNavCallbackFactory
from routes.users.misc.types.enum import Show, InlineWeekTypes, ScheduleTypes, ScheduleButtons, ModifyActions, Buidings
from routes.users.misc.types.named_tuple import PairNumbers
from routes.users.utils.types import PairTypes

back_button_text = "↩️Назад"

cancel_button_params = {
    "text": "❎Отменить",
    "callback_data": "return_to_learning_menu"
}

search_teacher_button_props = {
    "text": "👨‍🏫Поиск преподавателя",
    "switch_inline_query_current_chat": "teachers "
}


def learning_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text="📆Расписание", callback_data=ScheduleMenuCallbackFactory(type=ScheduleTypes.GROUP))
    builder.button(text="🔄Сменить группу", callback_data="change_group")
    builder.button(**search_teacher_button_props)

    builder.adjust(2, 1)

    return builder.as_markup()


def teacher_search_keyboard(teacher: Teachers.Model, schedule_type: ScheduleTypes) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if teacher.schedule:
        builder.button(
            text="📆Расписание преподавателя",
            callback_data=ScheduleMenuCallbackFactory(id=teacher.id, type=schedule_type)
        )

    builder.button(
        text="🪪Полная информация",
        url=teacher.full_info_url
    )

    builder.adjust(1)

    return builder.as_markup()


def schedule_menu(is_modify_allowed: Optional[bool] = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Сегодня",
        callback_data=ShowScheduleCallbackFactory(show=Show.TODAY)
    )

    builder.button(
        text="Завтра",
        callback_data=ShowScheduleCallbackFactory(show=Show.TOMORROW)
    )

    builder.button(
        text="Неделя",
        callback_data=ShowScheduleCallbackFactory(show=Show.WEEK)
    )
    if is_modify_allowed:
        builder.button(
            text="⚙️Редактировать",
            callback_data="modify_schedule"
        )

    builder.adjust(3)

    return builder.as_markup()


def back_to_schedule_menu(schedule_type: ScheduleTypes) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=back_button_text,
        callback_data=ScheduleMenuCallbackFactory(type=schedule_type)
    )

    return builder.as_markup()


def choose_day_menu(schedule_type: ScheduleTypes) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for index, btn in enumerate(ScheduleButtons):
        builder.button(
            text=btn.value,
            callback_data=ChooseDayCallBackFactory(weekday_index=index if index < 6 else "FULL")
        )

    builder.button(
        text=back_button_text,
        callback_data=ScheduleMenuCallbackFactory(type=schedule_type)
    )

    builder.adjust(6, 1, 1)

    return builder.as_markup()


def choose_week_type_menu(schedule_type: ScheduleTypes) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Текущее",
        callback_data=ChooseWeekTypeCallbackFactory(week_type=InlineWeekTypes.CURRENT)
    )

    builder.button(
        text="Полное",
        callback_data=ChooseWeekTypeCallbackFactory(week_type=InlineWeekTypes.FULL)
    )

    builder.button(
        text=back_button_text,
        callback_data=ScheduleMenuCallbackFactory(type=schedule_type)
    )

    builder.adjust(2, 1)

    return builder.as_markup()


def group_search_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(**cancel_button_params)

    return builder.as_markup()


def group_select_keyboard(groups: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for group in groups:
        builder.button(
            text=group,
            callback_data=SelectGroupCallbackFactory(selected_group=group)
        )

    builder.adjust(3)

    return builder.as_markup()


def schedule_find_group_error_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🔄Поиск группы",
        callback_data="change_group"
    )

    builder.adjust(1)

    return builder.as_markup()


def full_schedule_nav_keyboard_base(
        current_index: int,
        schedule_array_lenght: int,
) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="«",
        callback_data=FullScheduleNavCallbackFactory(index=0)
    )

    builder.button(
        text="‹",
        callback_data=FullScheduleNavCallbackFactory(
            index=current_index - 1
            if current_index > 0
            else schedule_array_lenght - 1
        )
    )

    builder.button(
        text="›",
        callback_data=FullScheduleNavCallbackFactory(
            index=current_index + 1
            if current_index + 1 < schedule_array_lenght
            else 0
        )
    )

    builder.button(
        text="»",
        callback_data=FullScheduleNavCallbackFactory(
            index=schedule_array_lenght - 1
        )
    )

    return builder


def full_schedule_nav_keyboard(
        current_index: int,
        schedule_array_lenght: int,
        schedule_type: ScheduleTypes
) -> InlineKeyboardMarkup:
    builder = full_schedule_nav_keyboard_base(
        current_index=current_index,
        schedule_array_lenght=schedule_array_lenght
    )

    builder.button(
        text=back_button_text,
        callback_data=ScheduleMenuCallbackFactory(type=schedule_type)
    )

    builder.adjust(4)

    return builder.as_markup()


def modify_schedule_actions_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Добавить",
        callback_data=ChooseModifyActionCallbackFactory(action=ModifyActions.ADD)
    )

    builder.button(
        text="Удалить",
        callback_data=ChooseModifyActionCallbackFactory(action=ModifyActions.REMOVE)
    )

    builder.button(
        text="Перенести",
        callback_data=ChooseModifyActionCallbackFactory(action=ModifyActions.TRANSFER)
    )

    builder.button(**cancel_button_params)
    builder.adjust(3, 1)

    return builder.as_markup()


def modify_schedule_weeks_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=f"{WeekBaseUpper.arrow.value}Нечетная",
        callback_data=ChooseModifyWeekCallbackFactory(week=InlineWeekTypes.UPPER)
    )

    builder.button(
        text=f"{WeekBaseLower.arrow.value}Четная",
        callback_data=ChooseModifyWeekCallbackFactory(week=InlineWeekTypes.LOWER)
    )

    builder.button(
        text="Обе",
        callback_data=ChooseModifyWeekCallbackFactory(week=InlineWeekTypes.FULL)
    )

    builder.button(**cancel_button_params)

    builder.adjust(3, 1)

    return builder.as_markup()


def full_schedule_nav_modify(
        current_index: int,
        schedule_array_lenght: int,
        pair_numbers_array: list[PairNumbers]
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for pair_number in pair_numbers_array:
        if pair_number.week == WeekBaseLower:
            week = InlineWeekTypes.LOWER
        elif pair_number.week == WeekBaseUpper:
            week = InlineWeekTypes.UPPER
        else:
            week = InlineWeekTypes.FULL

        cb = ChooseModifyPairCallbackFactory(
                day_index=current_index,
                week=week,
                number=pair_number.number
        )

        builder.button(
            text=f"{pair_number.week.arrow.value if pair_number.week else ''}{pair_number.number}",
            callback_data=cb
        )

    base = full_schedule_nav_keyboard_base(
        current_index=current_index,
        schedule_array_lenght=schedule_array_lenght
    )

    for row in base.as_markup().inline_keyboard:
        builder.add(*row)

    builder.button(**cancel_button_params)

    if pair_numbers_array:
        builder.adjust(len(pair_numbers_array), 4, 1)
    else:
        builder.adjust(4, 1)

    return builder.as_markup()


def choose_pair_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for pair_type in PairTypes:
        builder.button(
            text=pair_type.value,
            callback_data=ChoosePairTypeCallbackFactory(pair_type=pair_type)
        )

    builder.adjust(5)

    return builder.as_markup()


def find_pair_name_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🔎 Поиск пары",
        switch_inline_query_current_chat="pairs "
    )

    return builder.as_markup()


def confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅Подтвердить",
        callback_data="confirm"
    )

    builder.button(
        **cancel_button_params
    )

    return builder.as_markup()


def choose_building_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text=Buidings.BOLSHAYA_MORSKAYA.value,
        callback_data=ChooseBuildingCallbackFactory(building=Buidings.BOLSHAYA_MORSKAYA)
    )
    builder.button(
        text=Buidings.GASTELLO.value,
        callback_data=ChooseBuildingCallbackFactory(building=Buidings.GASTELLO)
    )
    builder.button(
        text=Buidings.LENSOVETA.value,
        callback_data=ChooseBuildingCallbackFactory(building=Buidings.LENSOVETA)
    )

    builder.adjust(1, 2)

    return builder.as_markup()


def choose_teacher_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(**search_teacher_button_props)
    return builder.as_markup()