from pprint import pprint

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent

from tgbot.models import QuizPart
from . import dp_user
from tgbot.bot.utils import get_texts, get_user
from ...keyboards import inline


@dp_user.inline_query(F.query.startswith("share"))
async def inline_mode_handler(inline_query: types.InlineQuery, state: FSMContext):

    user = await get_user(state, inline_query.from_user.id)
    texts = await get_texts(state)

    language = user.language if user.language else 'uz'
    query = inline_query.query

    link = query.split("_")[-1]
    quiz_part = QuizPart.objects.filter(link=link).select_related("quiz").first()

    if quiz_part:
        ques_text = texts['questions'][language]
        timer_text = texts['seconds'][language]
        result = [
            InlineQueryResultArticle(
                id=link,
                title=f"{quiz_part.quiz.title}",
                description=f"""
🖋 {quiz_part.to_number - quiz_part.from_number + 1} {ques_text} | ⏱ {quiz_part.quiz.timer}-{timer_text}
""",
                input_message_content=InputTextMessageContent(
                    message_text=f"""
<b>🎲 [{quiz_part.from_number} - {quiz_part.to_number}] {quiz_part.quiz.title}</b>

🖋 {quiz_part.to_number - quiz_part.from_number + 1} {ques_text} | ⏱ {quiz_part.quiz.timer}-{timer_text}
"""
                ),
                reply_markup=await inline.quiz_markup(texts, language, link, is_inline_query=True)
            )
        ]

        await inline_query.answer(results=result)

