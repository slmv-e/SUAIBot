from aiogram import Router
from routes.users.handlers import start, teacher_search, teacher_schedule, learning_menu, change_group, group_schedule, modify_schedule


def register_all_handlers(parent_router):
    parent_router.include_router(group_schedule.router)
    parent_router.include_router(start.router)
    parent_router.include_router(learning_menu.router)
    parent_router.include_router(teacher_search.router)
    parent_router.include_router(teacher_schedule.router)
    parent_router.include_router(change_group.router)
    parent_router.include_router(modify_schedule.router)


router = Router(name="users")
register_all_handlers(router)
