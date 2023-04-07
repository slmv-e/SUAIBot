from datetime import datetime

import aiogram.exceptions
from aiogram import Router, Bot, F, html
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from typing import Literal

from database import Teachers, Schedule
from database.Schedule import WeekTypes
from routes.users import utils
from routes.users.callback_factories import ScheduleMenuCallbackFactory, ShowScheduleCallbackFactory, Show, \
    ScheduleTypes, ChooseDayCallBackFactory, ChooseWeekTypeCallbackFactory, FullScheduleNavCallbackFactory, \
    InlineWeekTypes
from routes.users.states import WatchTeacherSchedule
from routes.users.keyboards.inline import schedule_menu, choose_day_menu, choose_week_type_menu, \
    full_schedule_nav_keyboard
from routes.users.misc.message_texts import teacher_schedule_menu_text
from routes.users.utils.schedule import handle_selected_day, get_info_message_text, get_week_type, filter_pairs

router = Router()


@router.callback_query(
    ScheduleMenuCallbackFactory.filter(F.type == ScheduleTypes.TEACHER),
    WatchTeacherSchedule.full
)
@router.callback_query(
    ScheduleMenuCallbackFactory.filter(F.type == ScheduleTypes.TEACHER),
    WatchTeacherSchedule.choose_week_type
)
@router.callback_query(
    ScheduleMenuCallbackFactory.filter(F.type == ScheduleTypes.TEACHER),
    WatchTeacherSchedule.watch_day
)
@router.callback_query(
    ScheduleMenuCallbackFactory.filter(F.type == ScheduleTypes.TEACHER),
    WatchTeacherSchedule.choose_day
)
async def teacher_schedule(
        callback: CallbackQuery,
        state: FSMContext
):
    await state.set_state(WatchTeacherSchedule.choose_day)

    try:
        await callback.message.edit_text(
            text=teacher_schedule_menu_text,
            reply_markup=schedule_menu()
        )
    except AttributeError:
        await callback.answer("⛔️Вы уже открыли расписание преподавателя")


@router.callback_query(
    ScheduleMenuCallbackFactory.filter(F.type == ScheduleTypes.TEACHER)
)
async def teacher_schedule(
        callback: CallbackQuery,
        callback_data: ScheduleMenuCallbackFactory,
        state: FSMContext,
        bot: Bot,
        teachers: list[Teachers.Model]
):
    selected_teacher: Teachers.Model
    selected_teacher, = filter(lambda teacher: teacher.id == callback_data.id, teachers)

    await bot.send_message(
        chat_id=callback.from_user.id,
        text=teacher_schedule_menu_text,
        reply_markup=schedule_menu()
    )

    await state.update_data(selected_teacher=selected_teacher)
    await state.set_state(WatchTeacherSchedule.choose_day)


@router.callback_query(
    WatchTeacherSchedule.choose_day,
    ShowScheduleCallbackFactory.filter()
)
async def chosen_day_teacher_schedule(
        callback: CallbackQuery,
        callback_data: ShowScheduleCallbackFactory,
        state: FSMContext,
        pairs_time: Schedule.PairsTime
):
    state_data = await state.get_data()
    selected_teacher: Teachers.Model = state_data.get("selected_teacher")

    today_index = datetime.today().weekday()

    # Bug fix: Issue #1
    current_week: WeekTypes = get_week_type(InlineWeekTypes.CURRENT)
    selected_teacher = Teachers.Model(
        **{
            **selected_teacher.dict(),
            "schedule": Schedule.BaseSchedule(
                **{
                    "week": filter_pairs(
                        week=selected_teacher.schedule.week,
                        filter_week=current_week
                    )
                }
            )
        }
    )

    if callback_data.show != Show.WEEK:
        await handle_selected_day(
            callback=callback,
            callback_data=callback_data,
            state=state,
            schedule=selected_teacher.schedule,
            pairs_time=pairs_time,
            state_group=WatchTeacherSchedule,
            schedule_type=ScheduleTypes.TEACHER,
            weekday_index=today_index
            if callback_data.show == Show.TODAY else
            today_index + 1 if today_index < 6 else 0
        )
    else:
        await callback.message.edit_text(
            text=f"📆 {html.bold(utils.schedule.current_day().value.upper())}\n"
                 "\n"
                 "Выберите день недели:",
            reply_markup=choose_day_menu(
                schedule_type=ScheduleTypes.TEACHER
            ),
            parse_mode="HTML"
        )


@router.callback_query(
    WatchTeacherSchedule.choose_day,
    ChooseDayCallBackFactory.filter()
)
async def choose_week_type(
        callback: CallbackQuery,
        callback_data: ChooseDayCallBackFactory,
        state: FSMContext
):
    await state.update_data(chosen_day=callback_data.weekday_index)

    weekdays_array = [weekday.value for weekday in Schedule.DayName]

    await callback.message.edit_text(
        text=f"📋Расписание на: "
             f"{html.italic(weekdays_array[callback_data.weekday_index + 1].lower()) if callback_data.weekday_index != 'FULL' else html.italic('неделя')}",
        reply_markup=choose_week_type_menu(
            schedule_type=ScheduleTypes.TEACHER
        ),
        parse_mode="HTML"
    )

    await state.set_state(WatchTeacherSchedule.choose_week_type)


@router.callback_query(
    WatchTeacherSchedule.choose_week_type,
    ChooseWeekTypeCallbackFactory.filter()
)
async def chosen_day_schedule(
        callback: CallbackQuery,
        callback_data: ChooseWeekTypeCallbackFactory,
        state: FSMContext,
        pairs_time: Schedule.PairsTime
):
    state_data = await state.get_data()
    selected_teacher: Teachers.Model = state_data.get("selected_teacher")
    chosen_weekday_index: int | Literal["FULL"] = state_data.get("chosen_day")

    # Bug fix: Issue #1
    selected_teacher = Teachers.Model(
        **{
            **selected_teacher.dict(),
            "schedule": Schedule.BaseSchedule(
                **{
                    "week": filter_pairs(
                        week=selected_teacher.schedule.week,
                        filter_week=callback_data.week_type
                    )
                }
            )
        }
    ) if callback_data.week_type != InlineWeekTypes.FULL else selected_teacher

    if isinstance(chosen_weekday_index, int):
        await handle_selected_day(
            callback=callback,
            callback_data=callback_data,
            state=state,
            schedule=selected_teacher.schedule,
            pairs_time=pairs_time,
            state_group=WatchTeacherSchedule,
            schedule_type=ScheduleTypes.TEACHER,
            weekday_index=chosen_weekday_index
        )
        await state.set_state(WatchTeacherSchedule.watch_day)
    else:
        await callback.message.edit_text(
            text=html.bold(f"1 из {len(selected_teacher.schedule.week)}\n\n") +
            get_info_message_text(
                day=selected_teacher.schedule.week[0],
                pairs_time=pairs_time,
                week_type_to_show=callback_data.week_type
            ),
            reply_markup=full_schedule_nav_keyboard(
                current_index=0,
                schedule_array_lenght=len(selected_teacher.schedule.week),
                schedule_type=ScheduleTypes.TEACHER
            ),
            parse_mode="HTML"
        )

        await state.update_data(selected_week_type=callback_data.week_type)
        await state.set_state(WatchTeacherSchedule.full)


@router.callback_query(
    WatchTeacherSchedule.full,
    FullScheduleNavCallbackFactory.filter()
)
async def full_schedule(
        callback: CallbackQuery,
        callback_data: FullScheduleNavCallbackFactory,
        state: FSMContext,
        pairs_time: Schedule.PairsTime
):
    state_data = await state.get_data()
    selected_teacher: Teachers.Model = state_data.get("selected_teacher")
    week_type: InlineWeekTypes = state_data.get("selected_week_type")

    # Bug fix: Issue #1
    selected_teacher = Teachers.Model(
        **{
            **selected_teacher.dict(),
            "schedule": Schedule.BaseSchedule(
                **{
                    "week": filter_pairs(
                        week=selected_teacher.schedule.week,
                        filter_week=week_type
                    )
                }
            )
        }
    ) if week_type != InlineWeekTypes.FULL else selected_teacher

    try:
        await callback.message.edit_text(
            text=html.bold(f"{callback_data.index + 1} из {len(selected_teacher.schedule.week)}\n\n") +
            get_info_message_text(
                day=selected_teacher.schedule.week[callback_data.index],
                pairs_time=pairs_time,
                week_type_to_show=week_type
            ),
            reply_markup=full_schedule_nav_keyboard(
                current_index=callback_data.index,
                schedule_array_lenght=len(selected_teacher.schedule.week),
                schedule_type=ScheduleTypes.TEACHER
            ),
            parse_mode="HTML"
        )
    except aiogram.exceptions.TelegramBadRequest:
        await callback.answer("⚠️ Вы уже находитесь на нужной странице")
