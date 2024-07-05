import asyncio
from pprint import pprint

from aiogram import Bot, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent

from tgbot.bot.keyboards import inline
from tgbot.bot.utils import get_user, get_texts
from tgbot.models import Quiz, QuizPart, UserQuizPart

from tgbot.bot.handlers.users import dp_user


@dp_user.message(F.text.regexp(r"^/[A-Z a-z 0-9]{10}$"))
async def send_quiz_parts(message: types.Message, bot: Bot, state: FSMContext):
    user = await get_user(state, message.from_user.id)
    texts = await get_texts(state)

    quiz_link = message.text.replace("/", "")
    parts = QuizPart.objects.filter(
        quiz__link=quiz_link, quiz__user__id=user.id
    ).select_related("quiz", "quiz__user").order_by("id")

    if parts:
        message_to_user = ""
        for index, part in enumerate(parts, start=1):
            message_to_user += f"<b>{index}</b>. <i>{part.quiz.title}</i> <b>[{part.from_number} - {part.to_number}]</b> 👉 /{part.link}\n"

        message_to_user += f"\n{texts['menu'][user.language]} 👉 /start"
        await message.answer(message_to_user)
    else:
        await message.delete()


@dp_user.message(F.text.regexp(r"^/[A-Z a-z 0-9]{12}$"))
async def send_quiz_questions(message: types.Message, bot: Bot, state: FSMContext):
    user = await get_user(state, message.from_user.id)
    texts = await get_texts(state)

    quiz_part_link = message.text.replace("/", "").split("_")[0]
    quiz_part = QuizPart.objects.filter(link=quiz_part_link)
    if quiz_part.exists():
        quiz: QuizPart = quiz_part.first()
        ques_text = texts['questions'][user.language]
        timer_text = texts['seconds'][user.language]
        message_to_user = f"""
[{quiz.from_number} - {quiz.to_number}] {quiz.quiz.title}
🖋 {quiz.to_number - quiz.from_number + 1} {ques_text} | ⏱ {quiz.quiz.timer}-{timer_text}
"""
        await message.answer(
            message_to_user,
            reply_markup=await inline.quiz_markup(texts, user.language, quiz_part_link)
        )

    else:
        await message.delete()


@dp_user.callback_query(F.data.startswith("quiz"))
async def start_quiz_callback(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    user = await get_user(state, call.message.chat.id)
    texts = await get_texts(state)

    link = call.data.split("__")[-1]
    quiz_part = QuizPart.objects.filter(link=link)
    if quiz_part.exists():
        quiz: QuizPart = quiz_part.first()
        questions = quiz.data['questions']
        ques_text = texts['questions'][user.language]
        timer_text = texts['duration'][user.language]
        message_to_user = f"""
🎲 {quiz.quiz.title}

🖋 {quiz.to_number - quiz.from_number + 1} {ques_text}
⏱ {str(timer_text).replace("_x_", f"{quiz.quiz.timer}")}

🏁 {texts['ready'][user.language]}
{str(texts['stop'][user.language]).replace('_command_', "/stop")}
"""
        await call.message.edit_text(
            message_to_user,
            reply_markup=await inline.generate_markup(
                {texts["_ready"][user.language]: f"ready_{link}"}
            )
        )
    await call.answer()


@dp_user.callback_query(F.data.startswith("ready"))
async def ready_test(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    user = await get_user(state, call.message.chat.id)
    texts = await get_texts(state)

    link = call.data.split("_")[-1]

    quiz_part = QuizPart.objects.filter(link=link)
    if quiz_part.exists():
        quiz_part = quiz_part.first()
        user_quiz_part = UserQuizPart.objects.create(
            user=user,
            quiz_part=quiz_part,
        )
        if user.data.get('current_quiz') is None:
            user.data['current_quiz'] = dict()
        user.data['current_quiz']['id'] = user_quiz_part.id
        index = user.data['current_quiz']['index'] = 0

        await call.message.delete_reply_markup()
        text = "3️⃣ ..."
        edited_message = await call.message.answer(text)
        for i in range(3):
            await asyncio.sleep(0.65)
            if i == 0:
                text = "2️⃣ ..."
            elif i == 1:
                text = "1️⃣ ..."
            else:
                text = "🚀 GO"
            edited_message = await bot.edit_message_text(
                text=text,
                chat_id=user.chat_id,
                message_id=edited_message.message_id)

        await bot.delete_message(chat_id=user.chat_id, message_id=edited_message.message_id)
        total_questions = len(quiz_part.data['questions'])
        question = quiz_part.data['questions'][index]['question']
        options = quiz_part.data['questions'][index]['options']
        correct_option = quiz_part.data['questions'][index]['correct_option']

        get_correct_option_id = lambda correct_option, options: [
            option_id for option_id, option in enumerate(options) if option == correct_option
        ][0]

        user.data['current_quiz']['total_questions'] = total_questions
        user.save(update_fields=['data'])

        await bot.send_poll(
            chat_id=user.chat_id,
            question=f"[{index + 1}/{total_questions}] {question}",
            options=options,
            correct_option_id=get_correct_option_id(correct_option, options),
            open_period=quiz_part.quiz.timer,
            is_anonymous=False,
            type="quiz",
            protect_content=True
        )
    else:
        await call.answer("NOT FOUND")

    await call.answer()


# @dp_user.message(F.text.in_(["3", "2", "1", "🚀 GO"]))
# async def start_quiz(message: types.Message, bot: Bot, state: FSMContext):
#     user = await get_user(state, message.from_user.id)
#     texts = await get_texts(state)
#
#     if message.text == "3":
#         await message.edit_text("2")
#
#     elif message.text == "2":
#         await message.edit_text("1")
#
#     elif message.text == "1":
#         await message.edit_text("🚀 GO")
#
#     print(message.text)

object