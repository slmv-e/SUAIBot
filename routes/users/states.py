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


class ModifyScheduleRemove(StatesGroup):
    choose_pair = State()
    confirm = State()


class ModifyScheduleTransfer(StatesGroup):
    choose_exist_pair = State()
    choose_week = State()
    choose_free_pair = State()
    choose_audience = State()
    confirm = State()


class ModifyScheduleAdd(StatesGroup):
    choose_free_pair = State()
    choose_pair_type = State()
    choose_pair_name = State()
    choose_building = State()
    choose_audience = State()
    choose_teachers = State()
    confirm = State()
