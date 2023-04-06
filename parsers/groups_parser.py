import requests
from bs4 import BeautifulSoup
from schedule_parser_module import parser_module
import database
import motor.motor_asyncio
from motor.core import Collection
import asyncio


async def main():
    mongo_url = "..."
    db_client: Collection = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)[database.name][
        database.CollectionNames.SCHEDULE.value]

    link = "https://guap.ru/rasp/"
    res = requests.get(link)
    soup = BeautifulSoup(res.text, 'html.parser')

    options = soup.find("select", {"name": "ctl00$cphMain$ctl05"})
    groups = list(filter(lambda e: e != "\n" and e["value"] != "-1", options.children))

    for group in groups:
        group_schedule_obj = parser_module(f"{link}?g={group['value']}")
        group_schedule_obj["group"] = group.text
        print(database.Schedule.Model(**group_schedule_obj))

        await db_client.insert_one(group_schedule_obj)


if __name__ == "__main__":
    asyncio.run(main())
