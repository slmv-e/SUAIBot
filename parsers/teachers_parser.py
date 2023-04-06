import requests
from bs4 import BeautifulSoup
from schedule_parser_module import parser_module


def main() -> dict:
    link = "https://guap.ru/rasp/"
    res = requests.get(link)
    soup = BeautifulSoup(res.text, 'html.parser')

    output = {}

    options = soup.find("select", {"name": "ctl00$cphMain$ctl06"})
    teachers = list(filter(lambda e: e != "\n" and e["value"] != "-1", options.children))

    for teacher in teachers:
        teacher_schedule_obj = parser_module(f"{link}?p={teacher['value']}")
        output[f"{teacher.text.split(' - ')[0].replace('.', ' ').strip()}"] = teacher_schedule_obj

    return output
