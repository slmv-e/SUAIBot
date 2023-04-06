import asyncio
import logging
import motor.motor_asyncio
from aiogram import Bot, Dispatcher

import database
from routes import users, admins
from filters.admin_filter import AdminFilter
from config import load_config, Config

logger = logging.getLogger(__name__)


def register_all_filters(config: Config):
    admins.router.message.filter(
        AdminFilter(
            ids=config.tgbot.admin_ids
        )
    )


def register_all_routers(dp: Dispatcher):
    dp.include_router(users.router)
    dp.include_router(admins.router)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")

    config = load_config(".env")
    bot = Bot(token=config.tgbot.token)
    dp = Dispatcher()
    db_client = motor.motor_asyncio.AsyncIOMotorClient(config.database.mongo_url)[database.name]

    teachers_preload: list[database.Teachers.Model] = await database.Teachers.handlers.get_all(db_client[database.CollectionNames.TEACHERS.value])
    groups_schedule_preload: list[database.Schedule.Model] = await database.Schedule.handlers.get_all(db_client[database.CollectionNames.SCHEDULE.value])

    register_all_filters(config)
    register_all_routers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(
        bot,
        db_client=db_client,
        teachers=teachers_preload,
        pairs_time=database.Schedule.PairsTime(),
        groups_schedule=groups_schedule_preload
    )


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
