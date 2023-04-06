from aiogram import html
from database import Teachers


def get_info_message_text(teacher: Teachers.Model) -> str:
    text_parts = [
        html.bold(teacher.name), ""
    ]

    if teacher.job_title:
        text_parts.append(f"{html.bold('Должность:')} {teacher.job_title}\n")

    if teacher.contacts:
        text_parts.append(html.bold("Контакты:"))
        if teacher.contacts.email:
            text_parts.append(f" - Email: {teacher.contacts.email}")
        if teacher.contacts.phone:
            text_parts.append(f" - Телефон: {teacher.contacts.phone}")
        if teacher.contacts.audience:
            text_parts.append(f" - Аудитория: {teacher.contacts.audience}")
        text_parts.append("")

    text_parts.append("<b>Позиции:</b>")
    for position in teacher.positions:
        text_parts.append(f" - {position.job_title}, {position.short_name}, {position.full_name}")

    return "\n".join(text_parts)
