import asyncio
import time
import random
from typing import Optional

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext

from tgbot.models import GroupQuizPart, Data
from tgbot.bot.handlers.utils import QuickSortListDict, get_time, username_filtering
from tgbot.bot.utils import get_texts
from tgbot.bot.keyboards.inline import share_markup


async def save_user_answer(current: dict, poll_answer: types.PollAnswer):
    user_id = poll_answer.user.id
    username = "@" + poll_answer.user.username if poll_answer.user.username else poll_answer.user.first_name
    end_time = round(time.perf_counter(), 1)

    group_quiz = GroupQuizPart.objects.filter(id=current['quiz_id']).select_related(
        "quiz_part", "quiz_part__quiz"
    ).first()
    if not group_quiz:
        return

    is_correct = False
    index = group_quiz.index

    if poll_answer.option_ids[0] == current['correct_option_id']:
        is_correct = True

    if not group_quiz.data['users'].get(str(user_id), None):
        group_quiz.data['users'][str(user_id)] = {
            "user_id": user_id,
            "username": username,
            "spend_time": 0,
            "corrects": 0,
            'wrongs': 0,
            'skips': 0,
            "quizzes": {}
        }

    current_user = group_quiz.data['users'][str(user_id)]

    if is_correct:
        current_user['corrects'] += 1
    else:
        current_user['wrongs'] += 1

    current_user['quizzes'][index] = {
        "is_correct": is_correct,
        "start_time": current['start_time'],
        "end_time": end_time,
        "spend_time": round(end_time - current['start_time'], 1)
    }
    current_user['spend_time'] += current_user['quizzes'][index]['spend_time']
    group_quiz.data['users'][str(user_id)] = current_user
    group_quiz.save(update_fields=['data'])


async def send_next_poll(group_quiz: Optional[GroupQuizPart], state: FSMContext, bot: Bot):
    group_quiz.index += 1
    group_quiz.save(update_fields=['index'])

    group_id = group_quiz.group_id
    index = group_quiz.index

    random.shuffle(group_quiz.data['questions'])

    quantity = group_quiz.quiz_part.quantity
    question = group_quiz.data['questions'][index]['question']
    options = group_quiz.quiz_part.data['questions'][index]['options']
    correct_option = group_quiz.quiz_part.data['questions'][index]['correct_option']

    random.shuffle(options)

    correct_option_id = lambda correct_option, options: [
        option_id for option_id, option in enumerate(options) if option == correct_option
    ][0]
    correct_option_id = correct_option_id(correct_option, options)

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

    poll_id = poll.poll.id
    data = Data.get_solo()
    if not data.data['groups'].get(str(poll_id), None):
        data.data['groups'][str(poll_id)] = dict()

    current = data.data['groups'][str(poll_id)]
    current['quiz_id'] = group_quiz.pk
    current['poll_id'] = poll.poll.id
    current['group_id'] = group_id
    current['start_time'] = round(time.perf_counter(), 1)
    current['correct_option_id'] = correct_option_id
    data.data['groups'][str(poll_id)] = current
    data.save()

    await asyncio.sleep(group_quiz.quiz_part.quiz.timer + 4)
    group_quiz = GroupQuizPart.objects.filter(id=group_quiz.pk).select_related(
        "quiz_part", "quiz_part__quiz", "data_model"
    ).first()

    if not group_quiz:
        return

    if group_quiz.is_active and not group_quiz.is_finish and group_quiz.index < group_quiz.quiz_part.quantity - 1:
        await save_user_skipped_answer(data, group_quiz, poll_id)
        return await send_next_poll(group_quiz, state, bot)

    group_quiz.is_finish = True
    await save_user_skipped_answer(data, group_quiz, poll_id)
    await send_users_statistics(group_quiz, state, bot)


async def send_users_statistics(group_quiz: Optional[GroupQuizPart], state: FSMContext, bot: Bot):
    texts = await get_texts(state)

    title = group_quiz.quiz_part.quiz.title
    language = group_quiz.language

    users = group_quiz.data['users']
    users_list = [user_data for user_data in users.values()]
    QuickSortListDict.quicksort(
        items=users_list,
        low=0,
        high=len(users_list) - 1,
        key1="corrects",
        key2="spend_time"
    )
    users_list.reverse()
    users_list_text = await get_users_list_text(
        users_list=users_list,
        texts=texts,
        language=language
    )

    msg = f"""
🏁 {title} {texts['test_end'][language]}
{users_list_text}

🏆 {texts['winners'][language]}!
"""

    await bot.send_message(
        chat_id=group_quiz.group_id,
        text=msg,
        reply_markup=await share_markup(texts, language, group_quiz.quiz_part.link)
    )


async def save_user_skipped_answer(data: Optional[Data], group_quiz: Optional[GroupQuizPart], poll_id: str):
    if not data:
        data = Data.get_solo()

    users = group_quiz.data['users']
    index = group_quiz.index

    current = data.data['groups'][poll_id]
    end_time = round(time.perf_counter(), 1)

    for user, user_data in users.items():
        quizzes = user_data['quizzes']
        if quizzes.get(index):
            continue

        quizzes[index] = {
            "is_correct": None,
            "start_time": current['start_time'],
            "end_time": end_time,
            "spend_time": round(end_time - current['start_time'], 1)
        }

        user_data['quizzes'] = quizzes
        user_data['skips'] += 1
    group_quiz.data['users'] = users
    group_quiz.save()


async def get_users_list_text(users_list: list, texts, language) -> str:
    users_list_text = ""
    for index, user_dict in enumerate(users_list):
        username = username_filtering(user_dict['username'])
        corrects = user_dict['corrects']
        spend_time = get_time(user_dict['spend_time'], texts, language)

        if index == 0:
            users_list_text += f"\n🥇 "
        elif index == 1:
            users_list_text += f"\n🥈 "

        elif index == 2:
            users_list_text += f"\n🥉 "

        else:
            users_list_text += f"\n{username} {corrects} ({spend_time})"
            continue

        users_list_text += f"{username} {corrects} ({spend_time})"
    return users_list_text


async def send_animation_numbers(group_id, call):
    await call.message.delete_reply_markup()
    text = "5️⃣ ..."
    edited_message = await call.message.answer(text)
    for i in range(5):
        await asyncio.sleep(0.65)
        if i == 0:
            text = "4️⃣ ..."
        elif i == 1:
            text = "3️⃣ ..."
        elif i == 2:
            text = "2️⃣ ..."
        elif i == 3:
            text = "1️⃣ ..."
        elif i == 4:
            text = "🚀 GO GO"
        edited_message = await call.bot.edit_message_text(
            text=text,
            chat_id=group_id,
            message_id=edited_message.message_id)
    await asyncio.sleep(0.65)
    await call.bot.delete_message(chat_id=group_id, message_id=edited_message.message_id)
