from database.Users import Model

dct = {
    "tg_id": 123,
    "group": "4218"
}

print(Model(**dct))