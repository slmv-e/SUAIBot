import dataclasses
from typing import Literal

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from datetime import date
from aiogram import html

from database import Schedule
from database.Schedule import Day, PairsTime, PairDetails, DayName, WeekBaseLower, WeekBaseUpper
from routes.users.callback_factories import InlineWeekTypes, ChooseWeekTypeCallbackFactory, ShowScheduleCallbackFactory, \
    ScheduleTypes
from routes.users.keyboards.inline import back_to_schedule_menu
from routes.users.states import WatchTeacherSchedule, WatchGroupSchedule


def current_day() -> DayName:
    for index, day in enumerate(DayName):
        if index == date.today().isoweekday():
            return day


def get_week_type(week_type_to_show: InlineWeekTypes) -> WeekBaseUpper | WeekBaseLower:
    if week_type_to_show == InlineWeekTypes.UPPER:
        return WeekBaseUpper
    elif week_type_to_show == InlineWeekTypes.LOWER:
        return WeekBaseLower
    else:
        days_different = date.today() - date(2022, 8, 29)
        return WeekBaseUpper if (days_different.days // 7 + 1) % 2 else WeekBaseLower


def get_info_message_text(day: Day, pairs_time: PairsTime, week_type_to_show: InlineWeekTypes) -> str:
    week_type: WeekBaseLower | WeekBaseUpper = get_week_type(week_type_to_show)
    text_parts = [f"{week_type.circle.value if week_type_to_show != InlineWeekTypes.FULL else '📆'} {html.bold(day.name.value.upper())}", ""]

    def add_upper():
        text_parts.append(
            f"{WeekBaseUpper.arrow.value} {html.bold(f'{pair.details.upper.type}-{pair.details.upper.name}')} ({html.code(', '.join(pair.details.upper.teacher_names))})")
        text_parts.append(f"{pair.details.upper.audience} ({html.code(', '.join(pair.details.upper.groups))})")

    def add_lower():
        text_parts.append(
            f"{WeekBaseLower.arrow.value} {html.bold(f'{pair.details.lower.type}-{pair.details.lower.name}')} ({html.code(', '.join(pair.details.lower.teacher_names))})")
        text_parts.append(f"{pair.details.lower.audience} ({', '.join(pair.details.lower.groups)})")

    for pair in day.pairs:
        try:
            text_parts.append(
                html.code(
                    f"🕚{pair.number} пара "
                    f"({pairs_time.at(pair.number).start.strftime('%H:%M')}-{pairs_time.at(pair.number).end.strftime('%H:%M')})"
                )
            )
        except TypeError:
            text_parts.append(html.code(f"⌚{pair.number}"))
        if isinstance(pair.details, PairDetails):
            text_parts.append(
                f"{html.bold(f'{pair.details.type} - {pair.details.name}')} " +
                (html.code(f"({', '.join(pair.details.teacher_names)})") if pair.details.teacher_names else "")
            )
            text_parts.append(pair.details.audience + " " + html.code(f"({', '.join(pair.details.groups)})"))
            text_parts.append("")
        elif week_type_to_show == InlineWeekTypes.FULL:
            pair.details.upper and add_upper()
            pair.details.lower and add_lower()
            text_parts.append("")
        elif week_type == WeekBaseUpper and pair.details.upper:
            add_upper()
            text_parts.append("")
        elif week_type == WeekBaseLower and pair.details.lower:
            add_lower()
            text_parts.append("")
        else:
            text_parts.pop(-1)

    return "\n".join(text_parts)


# Bug fix: Issue #1
def filter_pairs(
        week: list[Day],
        filter_week: WeekBaseUpper | WeekBaseLower
) -> list[Day]:
    week_filtered = list(
        filter(
            lambda day: any(
                isinstance(pair.details, PairDetails) or
                filter_week == WeekBaseUpper and pair.details.upper or
                filter_week == WeekBaseLower and pair.details.lower
                for pair in day.pairs
            ),
            week
        )
    )

    return week_filtered


async def handle_selected_day(
        callback: CallbackQuery,
        callback_data: ChooseWeekTypeCallbackFactory | ShowScheduleCallbackFactory,
        state: FSMContext,
        weekday_index: int,
        schedule: Schedule.Model,
        pairs_time: Schedule.PairsTime,
        schedule_type: ScheduleTypes,
        state_group: WatchGroupSchedule | WatchTeacherSchedule,
):
    try:
        weekday_schedule: Schedule.Day
        weekday_schedule, = filter(lambda day: day.weekday_index == weekday_index, schedule.week)
    except ValueError:
        await callback.message.edit_text(
            text="Выходной 😴",
            reply_markup=back_to_schedule_menu(
                schedule_type=schedule_type
            )
        )
    else:
        await callback.message.edit_text(
            text=get_info_message_text(weekday_schedule, pairs_time, callback_data.week_type),
            reply_markup=back_to_schedule_menu(
                schedule_type=schedule_type
            ),
            parse_mode="HTML"
        )
    await state.set_state(state_group.watch_day)


@dataclasses.dataclass
class AddActionPairDetails:
    number: int
    week: InlineWeekTypes
    day_index: int
    type: Literal["ПР", "ЛР", "Л", "КР", "КП"] = None
    name: str = None
    groups: list[str] = None
    audience: str = None
    teacher_names: list[str] = None
