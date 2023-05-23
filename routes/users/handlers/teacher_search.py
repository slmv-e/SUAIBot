from typing import NamedTuple
from aiogram import Router, F
from aiogram.types import InlineQuery
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.fsm.context import FSMContext
from fuzzywuzzy import fuzz

from database import Teachers
from routes.users.keyboards.inline import teacher_search_keyboard
from routes.users.callback_factories import ScheduleTypes
from routes.users.states import ModifyScheduleAdd
from routes.users.utils.teacher import get_info_message_text

router = Router()


class Search(NamedTuple):
    request: str
    results: list[InlineQueryResultArticle]


@router.inline_query(
    ModifyScheduleAdd.choose_teachers,
    F.query.startswith("teachers")
)
@router.inline_query(F.query.startswith("teachers"))
async def teacher_search(inline_query: InlineQuery, state: FSMContext, teachers: list[Teachers.Model]):
    offset = int(inline_query.offset) if inline_query.offset else 0
    _, *values = inline_query.query.split()
    search_request = " ".join(values)
    current_state = await state.get_state()

    state_data = await state.get_data()
    search_data = state_data.get("teacher_search")

    if not search_data or search_data.request != search_request:
        search_data = Search(
            request=search_request,
            results=[
                InlineQueryResultArticle(
                    id=teacher.id,
                    title=teacher.name,
                    description="Описание",
                    input_message_content=InputTextMessageContent(
                        message_text=teacher.name if current_state == ModifyScheduleAdd.choose_teachers else get_info_message_text(
                            teacher),
                        parse_mode="HTML"
                    ),
                    thumb_url=teacher.photo_url.replace(" ", "%20"),
                    photo_url=teacher.photo_url.replace(" ", "%20"),
                    reply_markup=teacher_search_keyboard(teacher, ScheduleTypes.TEACHER) if current_state != ModifyScheduleAdd.choose_teachers else None
                )
                for teacher in teachers
                if not search_request or fuzz.partial_ratio(search_request, teacher.name) >= 70
            ]
        )
        await state.update_data(teacher_search=search_data)

    if len(search_data.results) < 25:
        await inline_query.answer(
            search_data.results, is_personal=True, cache_time=0
        )
    elif offset < len(search_data.results):
        await inline_query.answer(
            search_data.results[offset: offset + 25], is_personal=True, cache_time=0,
            next_offset=str(offset + 25)
        )
    else:
        await inline_query.answer(
            search_data.results[offset:], is_personal=True, cache_time=0
        )
