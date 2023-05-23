import dataclasses
import hashlib

import aiogram.exceptions
from aiogram import Router, html, F
from aiogram.filters import Text
from aiogram.types import CallbackQuery, Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.fsm.context import FSMContext
from motor.motor_asyncio import AsyncIOMotorDatabase

from database import Users, CollectionNames, Schedule
from database.Schedule import DayName, Day, WeekBaseUpper, WeekBaseLower, PairDetails, Pair
from routes.users.handlers.learning_menu import learning_menu
from routes.users.handlers.teacher_search import Search
from routes.users.misc.message_texts import schedule_find_group_error_text
from routes.users.misc.types.enum import InlineWeekTypes, ModifyActions
from routes.users.misc.types.named_tuple import PairNumbers
from routes.users.states import ModifySchedule, ModifyScheduleTransfer, ModifyScheduleAdd, ModifyScheduleRemove
from routes.users.keyboards.inline import modify_schedule_actions_keyboard, schedule_find_group_error_keyboard, \
    modify_schedule_weeks_keyboard, full_schedule_nav_modify, choose_pair_type_keyboard, find_pair_name_keyboard, \
    confirm_keyboard, choose_building_keyboard, choose_teacher_keyboard
from routes.users.callback_factories import ChooseModifyActionCallbackFactory, ChooseModifyWeekCallbackFactory, \
    FullScheduleNavCallbackFactory, ChooseModifyPairCallbackFactory, \
    ChoosePairTypeCallbackFactory, ChooseBuildingCallbackFactory
from routes.users.utils.schedule import get_info_message_text, filter_pairs, AddActionPairDetails

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
                    week=WeekBaseUpper
                )
            )
            pair.details.lower and arr.append(
                PairNumbers(
                    number=pair.number,
                    week=WeekBaseLower
                )
            )
        elif week == InlineWeekTypes.UPPER and pair.details.upper:
            arr.append(
                PairNumbers(
                    number=pair.number,
                    week=WeekBaseUpper
                )
            )
        elif week == InlineWeekTypes.LOWER and pair.details.lower:
            arr.append(
                PairNumbers(
                    number=pair.number,
                    week=WeekBaseLower
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
                            week=WeekBaseLower
                        )
                    )
                elif week == InlineWeekTypes.UPPER:
                    arr.append(
                        PairNumbers(
                            number=pair_number,
                            week=WeekBaseUpper
                        )
                    )

    return arr


@router.callback_query(
    Text("modify_schedule"))
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
        if custom_schedule := await Users.handlers.get_user_custom_schedule(
                tg_id=callback.from_user.id,
                collection=db_client[CollectionNames.USERS.value]
        ):
            user_group_schedule = custom_schedule
        else:
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

    # Bug fix: Issue #1
    user_group_schedule = Schedule.Model.parse_obj(
        {
            **user_group_schedule.dict(),
            "week": filter_pairs(
                week=user_group_schedule.week,
                filter_week=callback_data.week
            )
        }
    ) if callback_data.week != InlineWeekTypes.FULL else user_group_schedule
    await state.update_data(user_group_schedule=user_group_schedule)

    week_lenght = len(user_group_schedule.week)
    if user_group_schedule.week[0].name == DayName.SCHEDULE_GRID_OUT and week_lenght < 7 or week_lenght < 6:
        week_names = [day_name for day_name in DayName]
        offset = int(user_group_schedule.week[0].name == DayName.SCHEDULE_GRID_OUT)

        exist_days = [None] * (6 + offset)
        for day in user_group_schedule.week:
            exist_days[day.weekday_index + offset] = day

        for ind, day in enumerate(exist_days):
            if not day:
                exist_days[ind] = Day(
                    name=week_names[ind + (1 - offset)],
                    weekday_index=ind + (1 - offset),
                    pairs=[]
                )

        empty_days_user_group_schedule = Schedule.Model.parse_obj(
            {
                **user_group_schedule.dict(),
                "week": exist_days
            }
        )
        if chosen_action == ModifyActions.ADD:
            user_group_schedule = empty_days_user_group_schedule
            week_lenght = len(exist_days)

    await state.update_data(empty_days_user_group_schedule=user_group_schedule)

    # нужен фикс (передача дня и длины массива недели)
    await callback.message.edit_text(
        text=html.bold(
            f"1 из {week_lenght}\n\n"
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
            pair_numbers_array=get_pairs_array(
                pairs_list=user_group_schedule.week[0].pairs,
                week=callback_data.week,
                chosen_action=chosen_action
            )
        ),
        parse_mode="HTML"
    )

    await state.update_data(selected_week_type=callback_data.week)
    if chosen_action == ModifyActions.ADD:
        await state.set_state(ModifyScheduleAdd.choose_free_pair)
    elif chosen_action == ModifyActions.REMOVE:
        await state.set_state(ModifyScheduleRemove.choose_pair)
    elif chosen_action == ModifyActions.TRANSFER:
        await state.set_state(ModifyScheduleTransfer.choose_exist_pair)


@router.callback_query(
    FullScheduleNavCallbackFactory.filter(),
    ModifyScheduleRemove.choose_pair
)
@router.callback_query(
    FullScheduleNavCallbackFactory.filter(),
    ModifyScheduleTransfer.choose_exist_pair
)
@router.callback_query(
    FullScheduleNavCallbackFactory.filter(),
    ModifyScheduleAdd.choose_free_pair
)
async def full_schedule(
        callback: CallbackQuery,
        callback_data: FullScheduleNavCallbackFactory,
        state: FSMContext,
        pairs_time: Schedule.PairsTime
):
    state_data = await state.get_data()
    week_type: InlineWeekTypes = state_data.get("selected_week_type")
    chosen_action: ModifyActions = state_data.get("modify_schedule_action")

    if await state.get_state() == ModifyScheduleAdd.choose_free_pair:
        user_group_schedule: Schedule.Model = state_data.get("empty_days_user_group_schedule")
    else:
        user_group_schedule = state_data.get("user_group_schedule")

    try:
        await callback.message.edit_text(
            text=html.bold(
                f"{callback_data.index + 1} из {len(user_group_schedule.week)}\n\n"
            ) + get_info_message_text(
                day=user_group_schedule.week[callback_data.index],
                pairs_time=pairs_time,
                week_type_to_show=week_type
            ) + html.bold(
                f"\nВыберите номер пары:"
            ),
            reply_markup=full_schedule_nav_modify(
                current_index=callback_data.index,
                schedule_array_lenght=len(user_group_schedule.week),
                pair_numbers_array=get_pairs_array(
                    pairs_list=user_group_schedule.week[callback_data.index].pairs,
                    week=week_type,
                    chosen_action=chosen_action
                )
            ),
            parse_mode="HTML"
        )
    except aiogram.exceptions.TelegramBadRequest:
        await callback.answer("⚠️ Вы уже находитесь на нужной странице")


@router.callback_query(
    ChooseModifyPairCallbackFactory.filter(),
    ModifyScheduleAdd.choose_free_pair
)
async def choose_free_pair_add(
        callback: CallbackQuery,
        callback_data: ChooseModifyPairCallbackFactory,
        state: FSMContext
):
    await state.update_data(pair_details=AddActionPairDetails(
        number=callback_data.number,
        week=callback_data.week,
        day_index=callback_data.day_index
    ))

    await callback.message.edit_text(
        text=html.bold("Выберите тип пары:"),
        reply_markup=choose_pair_type_keyboard(),
        parse_mode="HTML"
    )

    await state.set_state(ModifyScheduleAdd.choose_pair_type)


@router.callback_query(
    ChoosePairTypeCallbackFactory.filter(),
    ModifyScheduleAdd.choose_pair_type
)
async def choose_pair_type_add(
        callback: CallbackQuery,
        callback_data: ChoosePairTypeCallbackFactory,
        state: FSMContext
):
    state_data = await state.get_data()

    pair_details: AddActionPairDetails = state_data.get("pair_details")
    pair_details.type = callback_data.pair_type.value

    await state.update_data(pair_details=pair_details)

    await callback.message.edit_text(
        text=html.bold("Введите название пары:"),
        reply_markup=find_pair_name_keyboard(),
        parse_mode="HTML"
    )

    await state.set_state(ModifyScheduleAdd.choose_pair_name)


@router.inline_query(
    ModifyScheduleAdd.choose_pair_name,
    F.query.startswith("pairs")
)
async def pair_name_search(
        inline_query: InlineQuery,
        state: FSMContext
):
    state_data = await state.get_data()
    user_group_schedule: Schedule.Model = state_data.get("user_group_schedule")
    _, *values = inline_query.query.split()
    search_request = " ".join(values)

    pairs = [pair for day in user_group_schedule.week for pair in day.pairs]
    pairs_names = set()

    for pair in pairs:
        if isinstance(pair.details, PairDetails):
            pairs_names.add(pair.details.name)
        else:
            if pair.details.upper:
                pairs_names.add(pair.details.upper.name)
            if pair.details.lower:
                pairs_names.add(pair.details.lower.name)

    search_data = Search(
        request=search_request,
        results=[
            InlineQueryResultArticle(
                id=int(hashlib.md5(pair_name.encode()).hexdigest(), 16),
                title=pair_name,
                description="Описание",
                input_message_content=InputTextMessageContent(
                    message_text=pair_name,
                    parse_mode="HTML"
                ),
            )
            for pair_name in pairs_names
            if not search_request or search_request.lower() in pair_name.lower()
        ]
    )

    await inline_query.answer(search_data.results, is_personal=True)


@router.message(
    ModifyScheduleAdd.choose_pair_name
)
async def choose_pair_name(
        message: Message,
        state: FSMContext
):
    state_data = await state.get_data()

    pair_details: AddActionPairDetails = state_data.get("pair_details")
    pair_details.name = message.text.strip()

    await state.update_data(pair_details=pair_details)

    await message.answer(
        text=html.bold("Выберите корпус:"),
        reply_markup=choose_building_keyboard(),
        parse_mode="HTML"
    )

    await state.set_state(ModifyScheduleAdd.choose_building)


@router.callback_query(
    ChooseBuildingCallbackFactory.filter(),
    ModifyScheduleAdd.choose_building
)
async def choose_building(
        callback: CallbackQuery,
        callback_data: ChooseBuildingCallbackFactory,
        state: FSMContext
):
    state_data = await state.get_data()

    pair_details: AddActionPairDetails = state_data.get("pair_details")
    pair_details.audience = callback_data.building.value

    await state.update_data(pair_details=pair_details)

    await callback.message.edit_text(
        text=html.bold("Ввведите номер аудитории (Например: 24-12):"),
        parse_mode="HTML"
    )

    await state.set_state(ModifyScheduleAdd.choose_audience)


@router.message(
    ModifyScheduleAdd.choose_audience
)
async def choose_audience(
        message: Message,
        state: FSMContext
):
    state_data = await state.get_data()

    pair_details: AddActionPairDetails = state_data.get("pair_details")
    pair_details.audience += f", ауд. {message.text.strip()}"

    await state.update_data(pair_details=pair_details)

    await message.answer(
        text=html.bold("Введите имя преподавателя:"),
        reply_markup=choose_teacher_keyboard(),
        parse_mode="HTML"
    )

    await state.set_state(ModifyScheduleAdd.choose_teachers)


@router.message(
    ModifyScheduleAdd.choose_teachers
)
async def add_confirm(
        message: Message,
        state: FSMContext,
        pairs_time
):
    state_data = await state.get_data()

    pair_details: AddActionPairDetails = state_data.get("pair_details")
    pair_details.teacher_names = [message.text.strip()]

    user_group_schedule: Schedule.Model = state_data.get("empty_days_user_group_schedule")
    day_schedule = user_group_schedule.week[pair_details.day_index].copy(deep=True)

    pair_details.groups = [user_group_schedule.group]

    match pair_details.week:
        case InlineWeekTypes.FULL:
            day_schedule.pairs.append(
                Pair.parse_obj({
                    "number": pair_details.number,
                    "details": PairDetails.parse_obj(dataclasses.asdict(pair_details, dict_factory=dict))
                })
            )
        case InlineWeekTypes.UPPER:
            for pair in day_schedule.pairs:
                if pair.number == pair_details.number:
                    pair.details.upper = PairDetails.parse_obj(dataclasses.asdict(pair_details, dict_factory=dict))
                    break
            else:
                day_schedule.pairs.append(
                    Pair.parse_obj({
                        "number": pair_details.number,
                        "details": {
                            "upper": PairDetails.parse_obj(dataclasses.asdict(pair_details, dict_factory=dict))
                        }
                    })
                )
        case InlineWeekTypes.LOWER:
            for pair in day_schedule.pairs:
                if pair.number == pair_details.number:
                    pair.details.lower = PairDetails.parse_obj(dataclasses.asdict(pair_details, dict_factory=dict))
                    break
            else:
                day_schedule.pairs.append(
                    Pair.parse_obj({
                        "number": pair_details.number,
                        "details": {
                            "lower": PairDetails.parse_obj(dataclasses.asdict(pair_details, dict_factory=dict))
                        }
                    })
                )

    def replace_day(week: list[Day]):
        copied_week = week.copy()
        copied_week[pair_details.day_index] = day_schedule
        return copied_week

    await state.update_data(custom_schedule=Schedule.Model.parse_obj({
        "group": user_group_schedule.group,
        "week": replace_day(user_group_schedule.week)
    }))

    await message.answer(
        text=get_info_message_text(day_schedule, pairs_time, pair_details.week),
        parse_mode="HTML",
        reply_markup=confirm_keyboard()
    )

    await state.set_state(ModifyScheduleAdd.confirm)


@router.callback_query(
    ModifyScheduleAdd.confirm,
    Text("confirm")
)
async def confirm_add(
        callback: CallbackQuery,
        state: FSMContext,
        db_client: AsyncIOMotorDatabase
):
    state_data = await state.get_data()

    await Users.handlers.add_custom_schedule(
        tg_id=callback.from_user.id,
        custom_schedule=state_data.get("custom_schedule"),
        collection=db_client[CollectionNames.USERS.value]
    )

    await callback.message.edit_text(
        text="👍Пара успешно добавлена"
    )
    await learning_menu(callback.message, state)


@router.callback_query(
    ChooseModifyPairCallbackFactory.filter(),
    ModifyScheduleRemove.choose_pair
)
async def choose_pair_to_remove(
        callback: CallbackQuery,
        callback_data: ChooseModifyPairCallbackFactory,
        state: FSMContext,
        pairs_time
):
    state_data = await state.get_data()
    user_group_schedule: Schedule.Model = state_data.get("user_group_schedule")

    custom_schedule: Schedule.Model = user_group_schedule.copy(deep=True)

    for pair in custom_schedule.week[callback_data.day_index].pairs:
        if pair.number != callback_data.number:
            continue

        if callback_data.week == InlineWeekTypes.FULL:
            custom_schedule.week[callback_data.day_index].pairs.remove(pair)
        elif callback_data.week == InlineWeekTypes.LOWER:
            pair.details.lower = None
        elif callback_data.week == InlineWeekTypes.UPPER:
            pair.details.upper = None

    await state.update_data(custom_schedule=custom_schedule)

    await callback.message.answer(
        text=get_info_message_text(custom_schedule.week[callback_data.day_index], pairs_time, callback_data.week),
        parse_mode="HTML",
        reply_markup=confirm_keyboard()
    )

    await state.set_state(ModifyScheduleRemove.confirm)


@router.callback_query(
    ModifyScheduleRemove.confirm,
    Text("confirm")
)
async def confirm_remove_pair(
        callback: CallbackQuery,
        state: FSMContext,
        db_client: AsyncIOMotorDatabase
):
    state_data = await state.get_data()

    await Users.handlers.add_custom_schedule(
        tg_id=callback.from_user.id,
        custom_schedule=state_data.get("custom_schedule"),
        collection=db_client[CollectionNames.USERS.value]
    )

    await callback.message.edit_text(
        text="👍Пара успешно удалена"
    )
    await learning_menu(callback.message, state)
