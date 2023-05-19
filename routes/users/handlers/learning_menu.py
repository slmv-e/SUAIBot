from aiogram import Router
from aiogram.filters import Text
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from routes.users.keyboards.reply import MainMenuButtons
from routes.users.keyboards.inline import learning_menu_keyboard
from routes.users.misc.message_texts import learning_menu_text, action_cancel_success_text

router = Router()


@router.message(Text(MainMenuButtons.LEARNING.value))
async def learning_menu(
        message: Message,
        state: FSMContext
):
    await message.answer(
        text=learning_menu_text,
        reply_markup=learning_menu_keyboard()
    )

    await state.clear()


@router.callback_query(
    Text("return_to_learning_menu")
)
async def back_to_learning_menu(
        callback: CallbackQuery,
        state: FSMContext
):
    await callback.answer(
        text=action_cancel_success_text
    )
    await callback.message.edit_text(
        text=learning_menu_text,
        reply_markup=learning_menu_keyboard()
    )

    await state.clear()
