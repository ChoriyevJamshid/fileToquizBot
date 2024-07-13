import asyncio
import random
import time

from aiogram import Bot, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from tgbot.bot.handlers.utils import get_time

from tgbot.bot.keyboards import inline
from tgbot.bot.utils import get_user, get_texts
from tgbot.models import QuizPart, UserQuizPart

from tgbot.bot.handlers.users import dp_user


async def send_animation_numbers(user, call, bot):
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


async def save_user_quiz(chat_id: int | str, state: FSMContext, user_quiz: UserQuizPart) -> UserQuizPart:
    user = await get_user(state, chat_id)

    current = user.data['current']

    user_quiz.total_answers = len(current['answers'])
    user_quiz.correct_answers = current['corrects']
    user_quiz.skipped_answers = current['skips']
    user_quiz.failed_answers = current['wrongs']
    user_quiz.spend_time = sum([answer['spend_time'] for answer in current['answers']])
    user_quiz.data = current
    user_quiz.is_active = False
    user_quiz.save()
    return user_quiz


async def get_message_statistics(user_quiz: UserQuizPart, texts: dict, lg: str) -> str:
    msg_to_user = f"""
🏁 {user_quiz.quiz_part.quiz.title} {texts['test_end'][lg]}!

✅ {texts['correct'][lg]} - {user_quiz.correct_answers}
❌ {texts['no_correct'][lg]} - {user_quiz.failed_answers}
⌛️{texts['missed'][lg]} - {user_quiz.skipped_answers}

⏱ {get_time(user_quiz.spend_time, texts, lg)}
"""
    return msg_to_user


async def get_skipped_poll(chat_id: int | str, state: FSMContext, bot: Bot):
    user = await get_user(state, chat_id)
    current = user.data['current']
    texts = await get_texts(state)

    if current:
        current['_skips'] += 1
        if current['_skips'] == 2:
            current['_skips'] = -1
            user.data['current'] = current
            user.save(update_fields=['data'])

            return await bot.send_message(
                chat_id=user.chat_id,
                text=texts['skipped_answers_limit'][user.language],
                reply_markup=await inline.generate_markup(
                    buttons={
                        str(texts['continue'][user.language]): "continue"
                    }
                )
            )

        current['quiz']['index'] = current['i'] + 1
        current['quiz']['is_correct'] = None
        current['quiz']['is_skipped'] = True
        current['quiz']['end_time'] = round(time.perf_counter(), 1)
        current['quiz']['spend_time'] = current['quiz']['end_time'] - current['quiz']['start_time']
        current['quiz']['answer_option_id'] = None
        current['answers'].append(current['quiz'])
        current['skips'] += 1
        current['i'] += 1
        index = current['i']

        user_quiz: UserQuizPart = UserQuizPart.objects.filter(
            id=current['id']
        ).select_related('quiz_part', "quiz_part__quiz").first()
        quiz_part: QuizPart = user_quiz.quiz_part

        if index < quiz_part.quantity:
            quantity = quiz_part.quantity
            question = user.data['questions'][index]['question']
            options = quiz_part.data['questions'][index]['options']
            correct_option = quiz_part.data['questions'][index]['correct_option']

            random.shuffle(options)
            correct_option_id = lambda correct_option, options: [
                option_id for option_id, option in enumerate(options) if option == correct_option
            ][0]

            current['quiz']['correct_id'] = correct_option_id(correct_option, options)
            current['quiz']['start_time'] = round(time.perf_counter(), 1)
            user.data['current'] = current
            user.save(update_fields=['data'])

            await bot.send_poll(
                chat_id=user.chat_id,
                question=f"[{index + 1}/{quantity}] {question}",
                options=options,
                correct_option_id=correct_option_id(correct_option, options),
                open_period=quiz_part.quiz.timer,
                is_anonymous=False,
                type="quiz",
                protect_content=True
            )

            await asyncio.sleep(quiz_part.quiz.timer + 1)
            user = await get_user(state, chat_id)
            is_active = UserQuizPart.objects.filter(id=current['id']).first().is_active

            if is_active and len(user.data['current']['answers']) == index:
                await get_skipped_poll(chat_id, state, bot)
            return

        user.data['current'] = current
        user.save(update_fields=['data'])
        user_quiz: UserQuizPart = await save_user_quiz(chat_id, state, user_quiz)
        await bot.send_message(
            chat_id=user.chat_id,
            text=await get_message_statistics(user_quiz, texts, user.language),
            reply_markup=await inline.quiz_retry_markup(
                texts,
                user.language,
                user_quiz.quiz_part.link
            )
        )


@dp_user.message(Command("stop"))
async def quiz_part_stop(message: types.Message, state: FSMContext, bot: Bot):
    chat_id = message.chat.id
    user = await get_user(state, chat_id)
    texts = await get_texts(state)

    _user_quiz = UserQuizPart.objects.filter(user__chat_id=chat_id, is_active=True).first()
    if _user_quiz:
        user_quiz: UserQuizPart = await save_user_quiz(chat_id, state, _user_quiz)
        return await bot.send_message(
            chat_id=user.chat_id,
            text=await get_message_statistics(user_quiz, texts, user.language),
            reply_markup=await inline.quiz_retry_markup(
                texts,
                user.language,
                user_quiz.quiz_part.link
            )
        )

    await message.answer(text=f"🤖 {texts['no_test'][user.language]}")


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

{str(texts['stop_text'][user.language])}
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
    function = call.message.edit_text
    _, link = call.data.split("__")
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
        if _ == "quiz_retry":
            function = call.message.answer

        await function(
            message_to_user,
            reply_markup=await inline.generate_markup(
                {texts["_ready"][user.language]: f"ready_{link}"}
            )
        )
    await call.answer()


@dp_user.callback_query(F.data.startswith("ready"))
async def get_ready_link(call: types.CallbackQuery, state: FSMContext):
    chat_id = call.message.chat.id
    user = await get_user(state, chat_id)

    link = call.data.split("_")[-1]
    quiz_part: QuizPart = QuizPart.objects.filter(link=link).select_related("quiz").first()

    if quiz_part is not None:
        await send_animation_numbers(user, call, call.bot)

        user_quiz: UserQuizPart = UserQuizPart.objects.create(user=user, quiz_part=quiz_part)
        user.data['questions'] = quiz_part.data['questions']
        user.data['current'] = dict()
        user.data['current']['quiz'] = dict()
        user.data['current']['answers'] = list()
        user.data['current']['quantity'] = quiz_part.quantity
        user.data['current']['corrects'] = 0
        user.data['current']['skips'] = 0
        user.data['current']['_skips'] = 0
        user.data['current']['wrongs'] = 0
        user.data['current']['id'] = user_quiz.pk
        user.data['current']['is_active'] = user_quiz.is_active
        index = user.data['current']['i'] = 0

        random.shuffle(user.data['questions'])
        quantity = quiz_part.quantity
        question = user.data['questions'][index]['question']
        options = quiz_part.data['questions'][index]['options']
        correct_option = quiz_part.data['questions'][index]['correct_option']

        random.shuffle(options)
        correct_option_id = lambda correct_option, options: [
            option_id for option_id, option in enumerate(options) if option == correct_option
        ][0]

        user.data['current']['quiz']['correct_id'] = correct_option_id(correct_option, options)
        user.data['current']['quiz']['start_time'] = round(time.perf_counter(), 1)
        user.save(update_fields=['data'])

        await call.bot.send_poll(
            chat_id=user.chat_id,
            question=f"[{index + 1}/{quantity}] {question}",
            options=options,
            correct_option_id=correct_option_id(correct_option, options),
            open_period=quiz_part.quiz.timer,
            is_anonymous=False,
            type="quiz",
            protect_content=True
        )

        await asyncio.sleep(quiz_part.quiz.timer + 1)
        user = await get_user(state, chat_id)
        is_active = UserQuizPart.objects.filter(id=user_quiz.pk).first().is_active
        if is_active and len(user.data['current']['answers']) == index:
            await get_skipped_poll(chat_id, state, call.bot)


@dp_user.callback_query(F.data.startswith("continue"))
async def continue_poll(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    user = await get_user(state, call.message.chat.id)
    await call.message.delete()
    await get_skipped_poll(call.message.chat.id, state, call.bot)


@dp_user.poll_answer()
async def get_user_poll_answer(poll_answer: types.PollAnswer, state: FSMContext):

    chat_id = poll_answer.user.id
    user = await get_user(state, chat_id)
    texts = await get_texts(state)

    current = user.data.get('current', None)
    if current:
        is_correct = False
        if current['quiz']['correct_id'] == poll_answer.option_ids[0]:
            current['corrects'] += 1
            is_correct = True
        else:
            current['wrongs'] += 1

        current['quiz']['index'] = current['i']
        current['quiz']['is_correct'] = is_correct
        current['quiz']['is_skipped'] = False
        current['quiz']['end_time'] = round(time.perf_counter(), 1)
        current['quiz']['spend_time'] = round(current['quiz']['end_time'] - current['quiz']['start_time'], 1)
        current['quiz']['answer_option_id'] = poll_answer.option_ids[0]
        current['answers'].append(current['quiz'])
        current['i'] += 1
        index = current['i']

        user_quiz: UserQuizPart = UserQuizPart.objects.filter(
            id=current['id']
        ).select_related('quiz_part', "quiz_part__quiz").first()
        quiz_part: QuizPart = user_quiz.quiz_part

        if index < quiz_part.quantity:
            quantity = quiz_part.quantity
            question = user.data['questions'][index]['question']
            options = quiz_part.data['questions'][index]['options']
            correct_option = quiz_part.data['questions'][index]['correct_option']

            random.shuffle(options)
            correct_option_id = lambda correct_option, options: [
                option_id for option_id, option in enumerate(options) if option == correct_option
            ][0]

            current['quiz']['correct_id'] = correct_option_id(correct_option, options)
            current['quiz']['start_time'] = round(time.perf_counter(), 1)
            user.data['current'] = current
            user.save(update_fields=['data'])

            await poll_answer.bot.send_poll(
                chat_id=user.chat_id,
                question=f"[{index + 1}/{quantity}] {question}",
                options=options,
                correct_option_id=correct_option_id(correct_option, options),
                open_period=quiz_part.quiz.timer,
                is_anonymous=False,
                type="quiz",
                protect_content=True
            )

            await asyncio.sleep(quiz_part.quiz.timer + 1)
            user = await get_user(state, chat_id)
            is_active = UserQuizPart.objects.filter(id=current['id']).first().is_active

            if is_active and len(user.data['current']['answers']) == index:
                await get_skipped_poll(chat_id, state, poll_answer.bot)
            return
        user.data['current'] = current
        user.save(update_fields=['data'])
        user_quiz: UserQuizPart = await save_user_quiz(chat_id, state, user_quiz)
        await poll_answer.bot.send_message(
            chat_id=user.chat_id,
            text=await get_message_statistics(user_quiz, texts, user.language),
            reply_markup=await inline.quiz_retry_markup(
                texts,
                user.language,
                user_quiz.quiz_part.link
            )
        )
