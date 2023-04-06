from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Text
from motor.motor_asyncio import AsyncIOMotorDatabase

from routes.users.misc.message_texts import search_group, select_group_text
from routes.users.states import ChangeGroup
from routes.users.keyboards.inline import group_search_keyboard, group_select_keyboard
from routes.users.callback_factories import SelectGroupCallbackFactory
from database import Schedule, Users, CollectionNames

router = Router()


@router.callback_query(Text("change_group"))
async def change_group(
        callback: CallbackQuery,
        state: FSMContext,
):
    await callback.message.edit_text(
        text=search_group,
        reply_markup=group_search_keyboard(),
        parse_mode="HTML"
    )

    await state.set_state(ChangeGroup.search)


@router.message(
    ChangeGroup.search
)
async def select_group(
        message: Message,
        state: FSMContext,
        groups_schedule: list[Schedule.Model]
):
    found_groups = [
        group_schedule.group
        for group_schedule in groups_schedule
        if message.text.lower() in group_schedule.group.lower()
    ]

    await message.reply(
        text=select_group_text,
        reply_markup=group_select_keyboard(found_groups),
        parse_mode="HTML"
    )

    await state.set_state(ChangeGroup.select)


@router.callback_query(
    ChangeGroup.select,
    SelectGroupCallbackFactory.filter()
)
async def handle_selected_group(
        callback: CallbackQuery,
        callback_data: SelectGroupCallbackFactory,
        state: FSMContext,
        db_client: AsyncIOMotorDatabase
):
    await Users.handlers.change_user_group(
        callback.from_user.id,
        callback_data.selected_group,
        db_client[CollectionNames.USERS.value]
    )

    await callback.message.delete()

    await callback.message.answer(
        text=f"{callback.from_user.first_name}, ты зашел под группой {callback_data.selected_group}"
    )

    await state.clear()
