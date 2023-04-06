from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup
from enum import Enum


class MainMenuButtons(Enum):
    LEARNING = "Учеба"


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(
        text=MainMenuButtons.LEARNING.value
    )

    return builder.as_markup()
