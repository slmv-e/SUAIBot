import requests
from bs4 import BeautifulSoup
from database import Schedule


def parser_module(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    weekdays = [e.value for e in Schedule.DayName]

    obj = {
        "week": []
    }
    result_obj = soup.find("div", class_="result")
    for child in list(result_obj.children)[2:]:
        if child.name == "h3":
            obj["week"].append(
                {
                    "name": child.text,
                    "weekday_index": weekdays.index(child.text) - 1,
                    "pairs": []
                }
            )
        elif child.name == "h4":
            raw_text = child.text
            try:
                number, *_ = raw_text.split()
            except ValueError:
                obj["week"][-1]["pairs"].append({
                    "number": "вне сетки расписания",
                    "start_time": None,
                    "end_time": None
                })
            else:
                try:
                    obj["week"][-1]["pairs"].append({
                        "number": int(number)
                    })
                except ValueError:
                    obj["week"][-1]["pairs"].append({
                        "number": "вне сетки расписания"
                    })
        elif child.name == "div":
            raw_pair_type, name, audience = child.find("span").text.split(" – ")
            pair_type = raw_pair_type.split()[-1]

            details = {
                "name": name.strip(),
                "week_type": pair_type,
                "audience": audience.strip(",").strip(),
                "groups": list(map(lambda group: group.text, child.find("span", class_="groups").find_all("a"))),
                "teacher_names": list(map(lambda group: group.text.split(" - ")[0], child.find("span", class_="preps").find_all("a")))
                if child.find("span", class_="preps") else []
            }

            if len(list(child.find("span").children)) == 5:
                week_type_key = "upper" if child.find("b")['class'][0] == "up" else "lower"

                if "details" in obj["week"][-1]["pairs"][-1].keys():
                    obj["week"][-1]["pairs"][-1]["details"][week_type_key] = details
                else:
                    obj["week"][-1]["pairs"][-1]["details"] = {
                        week_type_key: details
                    }
            else:
                obj["week"][-1]["pairs"][-1]["details"] = details

    return obj
