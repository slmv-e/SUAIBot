from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup
from enum import Enum


class MainMenuButtons(Enum):
    LEARNING = "📝Учеба"
    SALES = "🎁Акции"
    NOTIFICATIONS = "🔔Уведомления"


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.button(
        text=MainMenuButtons.LEARNING.value
    )
    builder.button(
        text=MainMenuButtons.NOTIFICATIONS.value
    )
    builder.button(
        text=MainMenuButtons.SALES.value
    )

    return builder.as_markup()
