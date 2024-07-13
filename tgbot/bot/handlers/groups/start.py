import time
import asyncio
import random

from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from tgbot.bot.handlers.group_functions import (
    send_next_poll,
    send_animation_numbers
)
from tgbot.models import (
    QuizPart,
    GroupQuizPart,
    Data)
from tgbot.bot.filters.filter import ChatTypeFilter
from tgbot.bot.keyboards import inline
from tgbot.bot.utils import get_user, get_texts

dp_group = Router()
dp_group.message.filter(ChatTypeFilter(['group', 'supergroup']))


@dp_group.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    group_id = message.chat.id

    message_data = message.text.split(" ")
    user_id = message.from_user.id
    user = await get_user(state, user_id)
    texts = await get_texts(state)

    language = user.language
    if not language:
        language = 'uz'

    if len(message_data) < 2:
        return

    link = message_data[-1]
    quiz = QuizPart.objects.filter(link=link).first()

    if not quiz:
        return

    group_quiz, created = GroupQuizPart.objects.get_or_create(
        group_id=group_id,
        is_finish=False,
    )

    if not created:
        if group_quiz.is_active and not group_quiz.is_finish:
            group_quiz.is_active = False

        try:
            await message.bot.edit_message_reply_markup(
                chat_id=group_id,
                message_id=group_quiz.message_id,
                reply_markup=None
            )
        except Exception as e:
            print(f"\nException: {e}\n")
            pass

    if group_quiz.is_active:
        return await message.reply(
            text=texts['filter_text'][language]
        )
    group_quiz.data['questions'] = quiz.data['questions']
    group_quiz.message_id = message.message_id + 1
    group_quiz.language = language
    group_quiz.quiz_part = quiz
    group_quiz.save()

    ques_text = texts['questions'][language]
    timer_text = texts['seconds'][language]

    below_text = ""
    if group_quiz.data['users_number'] > 0:
        below_text += f"{texts['group_ready'][language]}: {group_quiz.data['users_number']}"

    msg = f"""
[{quiz.from_number} - {quiz.to_number}] {quiz.quiz.title}

🖋 {quiz.to_number - quiz.from_number + 1} {ques_text} 
⏱ {quiz.quiz.timer}-{timer_text}

{str(texts['start_in_group_2'][language])}.
👉 /stop {below_text}
"""
    return await message.answer(
        msg,
        reply_markup=await inline.generate_markup(
            {texts["_ready"][language]: f"group_{group_quiz.id}"}
        ))


@dp_group.message(Command("stop"))
async def stop_quiz(message: types.Message, state: FSMContext):
    group_id = message.chat.id
    user_id = message.from_user.id

    texts = await get_texts(state)

    group_quiz = GroupQuizPart.objects.filter(
        group_id=group_id,
        is_active=True,
        is_finish=False,
    ).select_related(
        "quiz_part", "quiz_part__quiz", "quiz_part__quiz__user"
    ).first()

    if not group_quiz:
        return await message.reply(
            text=f"🧐 {texts['no_test'][group_quiz.language]}"
        )

    if group_quiz.quiz_part.quiz.user.chat_id != user_id:
        return

    group_quiz.is_finish = True
    group_quiz.save()
    title = group_quiz.quiz_part.quiz.title
    return await message.reply(
        text=f"{title.title()} {texts['test_stop'][group_quiz.language]}"
    )


@dp_group.callback_query(F.data.startswith("group"))
async def ready_in_group(call: types.CallbackQuery, state: FSMContext):
    texts = await get_texts(state)

    bot = call.bot
    group_id = call.message.chat.id
    user_id = call.from_user.id
    username = "@" + call.from_user.username if call.from_user.username else call.from_user.first_name

    _, group_quiz_id = call.data.split("_")
    group_quiz = GroupQuizPart.objects.filter(id=group_quiz_id).select_related(
        "quiz_part", "quiz_part__quiz", "data_model"
    ).first()

    if not group_quiz:
        return

    if group_quiz.data['users'].get(str(user_id), None):
        return await call.answer()

    group_quiz.data['users'][str(user_id)] = {
        "user_id": user_id,
        "username": username,
        "spend_time": 0,
        "corrects": 0,
        'wrongs': 0,
        'skips': 0,
        "quizzes": {}
    }

    group_quiz.data['users_number'] += 1
    language = group_quiz.language
    ques_text = texts['questions'][language]
    timer_text = texts['seconds'][language]
    quiz = group_quiz.quiz_part

    msg = f"""
[{quiz.from_number} - {quiz.to_number}] {quiz.quiz.title}

🖋 {quiz.to_number - quiz.from_number + 1} {ques_text} 
⏱ {quiz.quiz.timer}-{timer_text}

{str(texts['start_in_group_2'][language])}.
👉 /stop . {texts['group_ready'][language]}: {group_quiz.data['users_number']}
    """

    await call.answer(texts["test_start_recently"][language])
    try:
        await bot.edit_message_text(
            text=msg,
            chat_id=group_id,
            message_id=group_quiz.message_id,
            reply_markup=await inline.generate_markup(
                {texts["_ready"][language]: f"group_{group_quiz.id}"}
            )
        )
    except Exception as e:
        print(f"\n{e}\n")

    if group_quiz.data['users_number'] <= 1:
        return group_quiz.save()

    group_quiz.is_active = True
    group_quiz.save()
    await asyncio.sleep(10)

    group_quiz = GroupQuizPart.objects.filter(id=group_quiz_id).select_related(
        "quiz_part", "quiz_part__quiz", "data_model"
    ).first()

    if not group_quiz.is_active:
        return

    random.shuffle(group_quiz.data['questions'])

    index = group_quiz.index
    quantity = group_quiz.quiz_part.quantity
    question = group_quiz.data['questions'][index]['question']
    options = group_quiz.quiz_part.data['questions'][index]['options']
    correct_option = group_quiz.quiz_part.data['questions'][index]['correct_option']

    random.shuffle(options)
    correct_option_id = lambda correct_option, options: [
        option_id for option_id, option in enumerate(options) if option == correct_option
    ][0]
    correct_option_id = correct_option_id(correct_option, options)

    await send_animation_numbers(group_id, call)
    poll = await bot.send_poll(
        chat_id=group_id,
        question=f"[{index + 1}/{quantity}]{question}",
        options=options,
        correct_option_id=correct_option_id,
        type="quiz",
        is_anonymous=False,
        open_period=group_quiz.quiz_part.quiz.timer,
        protect_content=False,
        allows_multiple_answers=False
    )

    poll_id: str = poll.poll.id
    data = Data.get_solo()

    if not data.data['groups'].get(poll_id, None):
        data.data['groups'][poll_id] = dict()

    current = data.data['groups'][poll_id]
    current['quiz_id'] = group_quiz.pk
    current['poll_id'] = poll.poll.id
    current['group_id'] = group_id
    current['start_time'] = round(time.perf_counter(), 1)
    current['correct_option_id'] = correct_option_id
    data.data['groups'][poll_id] = current
    data.save()

    await asyncio.sleep(group_quiz.quiz_part.quiz.timer + 1)
    group_quiz = GroupQuizPart.objects.filter(id=group_quiz.pk).select_related(
        "quiz_part", "quiz_part__quiz", "data_model"
    ).first()

    if not group_quiz:
        return

    if group_quiz.is_active and not group_quiz.is_finish and group_quiz.index < group_quiz.quiz_part.quantity - 1:
        await send_next_poll(group_quiz, state, bot)
