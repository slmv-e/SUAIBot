from typing import NamedTuple
from environs import Env


class DataBase(NamedTuple):
    mongo_url: str


class TgBot(NamedTuple):
    token: str
    admin_ids: list[int]


class Config(NamedTuple):
    tgbot: TgBot
    database: DataBase


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tgbot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS")))
        ),
        database=DataBase(
            mongo_url=env.str("MONGO_URL")
        )
    )
