import aiogram.exceptions
from aiogram import Router, html
from aiogram.filters import Text
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from motor.motor_asyncio import AsyncIOMotorDatabase

from database import Users, CollectionNames, Schedule
from database.Schedule import WeekTypes
from routes.users.misc.message_texts import schedule_find_group_error_text
from routes.users.states import ModifySchedule
from routes.users.keyboards.inline import modify_schedule_actions_keyboard, schedule_find_group_error_keyboard, \
    modify_schedule_weeks_keyboard, PairNumbers, full_schedule_nav_modify
from routes.users.callback_factories import ChooseModifyActionCallbackFactory, ChooseModifyWeekCallbackFactory, \
    InlineWeekTypes, FullScheduleNavCallbackFactory, ModifyActions
from routes.users.utils.schedule import get_info_message_text

router = Router()


def get_pairs_array(
        pairs_list: list[Schedule.Pair],
        week: InlineWeekTypes,
        chosen_action: ModifyActions
) -> list[PairNumbers]:
    arr = []

    for pair in pairs_list:
        if isinstance(pair.details, Schedule.PairDetails):
            arr.append(
                PairNumbers(
                    number=pair.number
                )
            )
        elif week == InlineWeekTypes.FULL:
            pair.details.upper and arr.append(
                PairNumbers(
                    number=pair.number,
                    week=WeekTypes.UPPER
                )
            )
            pair.details.lower and arr.append(
                PairNumbers(
                    number=pair.number,
                    week=WeekTypes.LOWER
                )
            )
        elif week == InlineWeekTypes.UPPER and pair.details.upper:
            arr.append(
                PairNumbers(
                    number=pair.number,
                    week=WeekTypes.UPPER
                )
            )
        elif week == InlineWeekTypes.LOWER and pair.details.lower:
            arr.append(
                PairNumbers(
                    number=pair.number,
                    week=WeekTypes.LOWER
                )
            )

    if chosen_action == ModifyActions.ADD:
        pair_numbers = [pair.number for pair in arr]
        arr = []
        if pair_numbers == ['вне сетки расписания']:
            return arr
        for pair_number in range(1, 8):
            if pair_number not in pair_numbers:
                if week == InlineWeekTypes.FULL:
                    arr.append(
                        PairNumbers(
                            number=pair_number
                        )
                    )
                elif week == InlineWeekTypes.LOWER:
                    arr.append(
                        PairNumbers(
                            number=pair_number,
                            week=WeekTypes.LOWER
                        )
                    )
                elif week == InlineWeekTypes.UPPER:
                    arr.append(
                        PairNumbers(
                            number=pair_number,
                            week=WeekTypes.UPPER
                        )
                    )

    return arr


@router.callback_query(
    Text("modify_schedule"))  # ДОБАВИТЬ УСЛОВИЕ "ЕСЛИ У ПОЛЬЗОВАТЕЛЯ ЕСТЬ МОДИФИЦИРОВАННОЕ РАСПИСАНИЕ"
async def modify_schedule_menu(
        callback: CallbackQuery,
        state: FSMContext,
        db_client: AsyncIOMotorDatabase,
        groups_schedule: list[Schedule.Model]
):
    if user_group := await Users.handlers.get_user_group(
            tg_id=callback.from_user.id,
            collection=db_client[CollectionNames.USERS.value]
    ):
        user_group_schedule: Schedule.Model
        user_group_schedule, = filter(lambda group_schedule: group_schedule.group == user_group, groups_schedule)

        await callback.message.edit_text(
            text="Выберите действие:",
            reply_markup=modify_schedule_actions_keyboard()
        )

        await state.update_data(user_group_schedule=user_group_schedule)
        await state.set_state(ModifySchedule.choose_action)
    else:
        await callback.message.edit_text(
            text=schedule_find_group_error_text,
            reply_markup=schedule_find_group_error_keyboard(),
            parse_mode="HTML"
        )


@router.callback_query(
    ModifySchedule.choose_action,
    ChooseModifyActionCallbackFactory.filter()
)
async def handle_chosen_action(
        callback: CallbackQuery,
        callback_data: ChooseModifyActionCallbackFactory,
        state: FSMContext
):
    await callback.message.edit_text(
        text="Выберите неделю:",
        reply_markup=modify_schedule_weeks_keyboard()
    )

    await state.update_data(modify_schedule_action=callback_data.action)
    await state.set_state(ModifySchedule.choose_week)


@router.callback_query(
    ModifySchedule.choose_week,
    ChooseModifyWeekCallbackFactory.filter()
)
async def handle_chosen_week(
        callback: CallbackQuery,
        callback_data: ChooseModifyWeekCallbackFactory,
        state: FSMContext,
        pairs_time: Schedule.PairsTime
):
    state_data = await state.get_data()

    user_group_schedule: Schedule.Model = state_data.get("user_group_schedule")
    chosen_action: ModifyActions = state_data.get("modify_schedule_action")

    arr = get_pairs_array(
        pairs_list=user_group_schedule.week[0].pairs,
        week=callback_data.week,
        chosen_action=chosen_action
    )

    await callback.message.edit_text(
        text=html.bold(
            f"1 из {len(user_group_schedule.week)}\n\n"
        ) + get_info_message_text(
            day=user_group_schedule.week[0],
            pairs_time=pairs_time,
            week_type_to_show=callback_data.week
        ) + html.bold(
            f"\nВыберите номер пары:"
        ),
        reply_markup=full_schedule_nav_modify(
            current_index=0,
            schedule_array_lenght=len(user_group_schedule.week),
            pair_numbers_array=arr
        ),
        parse_mode="HTML"
    )

    await state.update_data(selected_week_type=callback_data.week)
    await state.set_state(ModifySchedule.choose_pair)


@router.callback_query(
    ModifySchedule.choose_pair,
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
    chosen_action: ModifyActions = state_data.get("modify_schedule_action")

    arr = get_pairs_array(
        pairs_list=user_group_schedule.week[callback_data.index].pairs,
        week=week_type,
        chosen_action=chosen_action
    )

    try:
        await callback.message.edit_text(
            text=html.bold(f"{callback_data.index + 1} из {len(user_group_schedule.week)}\n\n") +
            get_info_message_text(
                day=user_group_schedule.week[callback_data.index],
                pairs_time=pairs_time,
                week_type_to_show=week_type
            ) + html.bold(
                f"\nВыберите номер пары:"
            ),
            reply_markup=full_schedule_nav_modify(
                current_index=callback_data.index,
                schedule_array_lenght=len(user_group_schedule.week),
                pair_numbers_array=arr
            ),
            parse_mode="HTML"
        )
    except aiogram.exceptions.TelegramBadRequest:
        await callback.answer("⚠️ Вы уже находитесь на нужной странице")
