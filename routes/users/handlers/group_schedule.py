from datetime import datetime
from typing import Literal

import aiogram.exceptions
from aiogram import Router, F, html
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from motor.motor_asyncio import AsyncIOMotorDatabase

from routes.users import utils
from routes.users.callback_factories import ScheduleMenuCallbackFactory, ScheduleTypes, \
    ShowScheduleCallbackFactory, Show, ChooseDayCallBackFactory, ChooseWeekTypeCallbackFactory, \
    FullScheduleNavCallbackFactory, InlineWeekTypes
from routes.users.keyboards.inline import schedule_menu, schedule_find_group_error_keyboard, \
    choose_day_menu, choose_week_type_menu, full_schedule_nav_keyboard
from routes.users.misc.message_texts import schedule_find_group_error_text, group_schedule_menu_text
from routes.users.states import WatchGroupSchedule
from database import Schedule, Users, CollectionNames
from routes.users.utils.schedule import handle_selected_day, get_info_message_text

router = Router()


@router.callback_query(
    ScheduleMenuCallbackFactory.filter(F.type == ScheduleTypes.GROUP)
)
async def user_group_schedule_menu(
        callback: CallbackQuery,
        state: FSMContext,
        groups_schedule: list[Schedule.Model],
        db_client: AsyncIOMotorDatabase
):
    if user_group := await Users.handlers.get_user_group(
            tg_id=callback.from_user.id,
            collection=db_client[CollectionNames.USERS.value]
    ):
        user_group_schedule: Schedule.Model
        user_group_schedule, = filter(lambda group_schedule: group_schedule.group == user_group, groups_schedule)

        await callback.message.edit_text(
            text=group_schedule_menu_text + html.bold(user_group),
            reply_markup=schedule_menu(
                is_modify_allowed=True
            ),
            parse_mode="HTML"
        )

        await state.update_data(user_group_schedule=user_group_schedule)
        await state.set_state(WatchGroupSchedule.choose_day)
    else:
        await callback.message.edit_text(
            text=schedule_find_group_error_text,
            reply_markup=schedule_find_group_error_keyboard(),
            parse_mode="HTML"
        )


@router.callback_query(
    WatchGroupSchedule.choose_day,
    ShowScheduleCallbackFactory.filter()
)
async def chosen_day_user_group_schedule(
        callback: CallbackQuery,
        callback_data: ShowScheduleCallbackFactory,
        state: FSMContext,
        pairs_time: Schedule.PairsTime
):
    state_data = await state.get_data()
    user_group_schedule: Schedule.Model = state_data.get("user_group_schedule")

    today_index = datetime.today().weekday()

    if callback_data.show != Show.WEEK:
        await handle_selected_day(
            callback=callback,
            callback_data=callback_data,
            state=state,
            schedule=user_group_schedule,
            pairs_time=pairs_time,
            state_group=WatchGroupSchedule,
            schedule_type=ScheduleTypes.GROUP,
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
                schedule_type=ScheduleTypes.GROUP
            ),
            parse_mode="HTML"
        )


@router.callback_query(
    WatchGroupSchedule.choose_day,
    ChooseDayCallBackFactory.filter()
)
async def choose_week_type(
        callback: CallbackQuery,
        callback_data: ChooseDayCallBackFactory,
        state: FSMContext
):
    weekdays_array = [weekday.value for weekday in Schedule.DayName]

    await callback.message.edit_text(
        text=f"📋Расписание на: "
             f"{html.italic(weekdays_array[callback_data.weekday_index + 1].lower()) if callback_data.weekday_index != 'FULL' else html.italic('неделя')}",
        reply_markup=choose_week_type_menu(
            schedule_type=ScheduleTypes.GROUP
        ),
        parse_mode="HTML"
    )

    await state.update_data(chosen_day=callback_data.weekday_index)
    await state.set_state(WatchGroupSchedule.choose_week_type)


@router.callback_query(
    WatchGroupSchedule.choose_week_type,
    ChooseWeekTypeCallbackFactory.filter()
)
async def chosen_day_schedule(
        callback: CallbackQuery,
        callback_data: ChooseWeekTypeCallbackFactory,
        state: FSMContext,
        pairs_time: Schedule.PairsTime
):
    state_data = await state.get_data()
    user_group_schedule: Schedule.Model = state_data.get("user_group_schedule")
    chosen_weekday_index: int | Literal["FULL"] = state_data.get("chosen_day")

    if isinstance(chosen_weekday_index, int):
        await handle_selected_day(
            callback=callback,
            callback_data=callback_data,
            state=state,
            schedule=user_group_schedule,
            pairs_time=pairs_time,
            state_group=WatchGroupSchedule,
            schedule_type=ScheduleTypes.GROUP,
            weekday_index=chosen_weekday_index
        )
        await state.set_state(WatchGroupSchedule.watch_day)
    else:
        await callback.message.edit_text(
            text=html.bold(f"1 из {len(user_group_schedule.week)}\n\n") +
            get_info_message_text(
                day=user_group_schedule.week[0],
                pairs_time=pairs_time,
                week_type_to_show=callback_data.week_type
            ),
            reply_markup=full_schedule_nav_keyboard(
                current_index=0,
                schedule_array_lenght=len(user_group_schedule.week),
                schedule_type=ScheduleTypes.GROUP
            ),
            parse_mode="HTML"
        )

        await state.update_data(selected_week_type=callback_data.week_type)
        await state.set_state(WatchGroupSchedule.full)


@router.callback_query(
    WatchGroupSchedule.full,
    FullScheduleNavCallbackFactory.filter()
)
async def full_schedule(
        callback: CallbackQuery,
        callback_data: FullScheduleNavCallbackFactory,
        state: FSMContext,
        pairs_time: Schedule.PairsTime
):
    state_data = await state.get_data()
    user_group_schedule: Schedule.Model = state_data.get("user_group_schedule")
    week_type: InlineWeekTypes = state_data.get("selected_week_type")

    try:
        await callback.message.edit_text(
            text=html.bold(f"{callback_data.index + 1} из {len(user_group_schedule.week)}\n\n") +
            get_info_message_text(
                day=user_group_schedule.week[callback_data.index],
                pairs_time=pairs_time,
                week_type_to_show=week_type
            ),
            reply_markup=full_schedule_nav_keyboard(
                current_index=callback_data.index,
                schedule_array_lenght=len(user_group_schedule.week),
                schedule_type=ScheduleTypes.GROUP
            ),
            parse_mode="HTML"
        )
    except aiogram.exceptions.TelegramBadRequest:
        await callback.answer("⚠️ Вы уже находитесь на нужной странице")
