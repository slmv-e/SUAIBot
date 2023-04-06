from aiogram import html

start_text = "Привет! Я SUAI-Bot"
learning_menu_text = "Меню учёбы"
teacher_schedule_menu_text = "🗓️Меню расписания преподавателя"
group_schedule_menu_text = "🗓️Меню расписания группы\n\n" \
                           "Выбранная группа: "
search_group = f"Введите {html.bold('часть')} группы (42) или ее {html.bold('полный')} номер (4218)\n\n" \
               f"{html.italic('Либо отмените поиск кнопкой ниже:')}"
select_group_text = f"🔎 {html.italic('Найденные группы: ')}"
action_cancel_success_text = "👍 Действие отменено!"
schedule_find_group_error_text = f"⛔️Для выполнения данного действия следует {html.bold('выбрать')} группу"
