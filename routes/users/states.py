from aiogram.fsm.state import StatesGroup, State


class WatchTeacherSchedule(StatesGroup):
    choose_day = State()
    watch_day = State()
    choose_week_type = State()
    full = State()


class WatchGroupSchedule(StatesGroup):
    choose_day = State()
    watch_day = State()
    choose_week_type = State()
    full = State()


class ChangeGroup(StatesGroup):
    search = State()
    select = State()


class ModifySchedule(StatesGroup):
    choose_action = State()
    choose_week = State()
    choose_pair = State()