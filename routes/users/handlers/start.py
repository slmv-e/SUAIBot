from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from motor.motor_asyncio import AsyncIOMotorDatabase

import database
from routes.users.keyboards.reply import main_menu_keyboard
from routes.users.misc.message_texts import start_text
from database import Users

router = Router(name="start_handler")


@router.message(Command("start"))
async def start(
        message: Message,
        state: FSMContext,
        db_client: AsyncIOMotorDatabase
):

    await Users.handlers.insert_new_user(
        tg_id=message.from_user.id,
        collection=db_client[database.CollectionNames.USERS.value]
    )

    await message.answer(
        text=start_text,
        reply_markup=main_menu_keyboard()
    )

    await state.clear()
