import requests
from bs4 import BeautifulSoup
import teachers_parser
import database
import motor.motor_asyncio
from motor.core import Collection
import asyncio


async def main():
    mongo_url = "..."
    db_client: Collection = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)[database.name][database.CollectionNames.TEACHERS.value]

    teachers_schedule_obj = teachers_parser.main()

    for i in range(1, 107 + 1):
        res = requests.get(f"https://pro.guap.ru/professors?page={i}")
        soup = BeautifulSoup(res.text, 'html.parser')
        teacher_cards = soup.select(".card.my-sm-2")
        for card in teacher_cards:
            path = card.select_one("a")["href"]
            full_info_url = f"https://pro.guap.ru{path}"
            card_res = requests.get(full_info_url)
            card_soup = BeautifulSoup(card_res.text, 'html.parser')

            full_name = " ".join(card_soup.select_one("#fio").text.replace("\n", " ").split())
            surname, *other_names = full_name.split()
            schedule_key = f"{surname} {' '.join([name[0] for name in other_names])}"
            profile_image_link = f"https://pro.guap.ru{card_soup.select_one('.profile_image')['src']}"
            try:
                job_title = " ".join(card_soup.select_one(".badge.mt-2").text.replace("\n", " ").split())
            except AttributeError:
                job_title = None

            _, *contacts_obj, positions_obj = card_soup.select(".card.shadow-sm")

            contacts = None

            if contacts_obj:
                try:
                    email = card_soup.find(string="Email").parent.findNext().text
                except AttributeError:
                    email = None
                try:
                    audience = card_soup.find(string="Аудитория").parent.findNext().text
                except AttributeError:
                    audience = None
                try:
                    phone = card_soup.find(string="Телефон").parent.findNext().text
                except AttributeError:
                    phone = None

                contacts = {
                    "email": email,
                    "phone": phone,
                    "audience": audience
                }

            positions_list = list(positions_obj.select(".list-group-item"))[1:]
            positions = []
            for pos in positions_list:
                positions.append({
                    "short_name": pos.select_one("small").text,
                    "job_title": pos.select_one("h5").text,
                    "full_name": pos.select_one("div.small").text
                })

            obj = {
                "id": int(path.split("/")[-1]),
                "name": full_name,
                "photo_url": profile_image_link,
                "job_title": job_title,
                "contacts": contacts,
                "positions": positions,
                "full_info_url": full_info_url,
                "schedule": teachers_schedule_obj.get(schedule_key)
            }

            await db_client.insert_one(obj)

if __name__ == '__main__':
    asyncio.run(main())
