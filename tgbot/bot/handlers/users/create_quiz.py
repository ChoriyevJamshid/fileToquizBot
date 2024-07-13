import os
import random

from aiogram import Bot, types, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from django.conf import settings

from tgbot.bot.keyboards import reply, inline
from tgbot.bot.states.main import NewQuizState
from tgbot.bot.engine import reader
from tgbot.bot.utils import get_texts, get_user

from tgbot.models import Quiz, QuizPart
from tgbot.bot.handlers.users import dp_user
from tgbot.bot.handlers.utils import generate_random_string


def create_quiz_part(quiz, ques_count, quiz_part_list):
    while True:
        new_link = generate_random_string(length=12)
        if not QuizPart.objects.filter(link=new_link).exists():
            break

    from_number = ques_count - 24 if ques_count - 24 > 0 else 1

    quiz_part = QuizPart.objects.create(
        quiz_id=quiz.id,
        link=new_link,
        from_number=from_number,
        to_number=ques_count,
    )
    quiz_part.data['questions'] = quiz_part_list
    quiz_part.save()


async def save_data(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    user = await get_user(state, message.from_user.id)
    texts = await get_texts(state)
    try:
        while True:
            new_link = generate_random_string()
            if not Quiz.objects.filter(link=new_link).exists():
                break
        quiz = Quiz.objects.create(
            user_id=user.id,
            title=data.get("test_title"),
            timer=data.get("test_duration"),
            link=new_link,
        )

    except Exception as e:
        print(f"Exception: {e}")
        return await message.answer(
            texts['quiz_title_unique'][user.language],
            reply_markup=types.ReplyKeyboardRemove()
        )

    if quiz:
        quiz_part_list = list()
        question_data = None
        ques_count = 0
        is_correct = False
        for index, value in enumerate(data.get("test_questions"), start=1):

            if index % 5 == 1:
                ques_count += 1
                question_data = dict()
                question_data['question'] = str(value)
                question_data['options'] = []
                is_correct = True
            else:
                question_data['options'].append(str(value))
                if is_correct:
                    question_data['correct_option'] = str(value)
                    is_correct = False

                if index % 5 == 0:
                    quiz_part_list.append(question_data)
                    if ques_count % 25 == 0:
                        create_quiz_part(quiz, ques_count, quiz_part_list)
                        quiz_part_list = list()

        if 0 < len(quiz_part_list) < 25:
            create_quiz_part(quiz, ques_count, quiz_part_list)

        quiz.quantity = ques_count
        quiz.save(update_fields=['quantity'])

        message_to_user = texts['test_created'][user.language]
        await message.answer(message_to_user, reply_markup=types.ReplyKeyboardRemove())
    else:
        pass

    await state.clear()


@dp_user.message(NewQuizState.title)
async def new_quiz_title(message: types.Message, state: FSMContext):
    texts = await get_texts(state)
    user = await get_user(state, message.from_user.id)
    if message.content_type == ContentType.TEXT:

        if Quiz.objects.filter(title=message.text, user=user).exists():
            await message.answer(
                texts['quiz_title_unique'][user.language],
                reply_markup=await inline.generate_markup({"🔙": "back"})
            )
        else:
            await state.update_data(test_title=message.text)

            message_to_user = texts['test_file'][user.language]
            await message.answer(message_to_user, reply_markup=await inline.generate_markup({"🔙": "back"}))
            await state.set_state(NewQuizState.file)
    else:
        message_to_user = texts['write_text'][user.language]
        await message.answer(message_to_user)


@dp_user.message(NewQuizState.file)
async def new_quiz_file(message: types.Message, bot: Bot, state: FSMContext):
    texts = await get_texts(state)
    user = await get_user(state, message.from_user.id)

    if message.content_type == ContentType.DOCUMENT:
        os.makedirs(f"{settings.BASE_DIR}/media", exist_ok=True)

        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        _format = file.file_path.split('.')[-1]
        new_file = f"{file.file_id}.{_format}"
        await bot.download_file(file.file_path, f"media/{new_file}")

        if _format in ('xls', 'xlsx', 'docx', 'csv', 'txt'):
            try:
                questions = []
                if _format in ('xls', 'xlsx'):
                    questions = await reader.get_excel_content(
                        f"{settings.BASE_DIR}/media/{new_file}",
                        _format=_format
                    )
                elif _format == 'docx':
                    questions = await reader.get_docx_content(
                        f"{settings.BASE_DIR}/media/{new_file}"
                    )
                elif _format == "csv":
                    questions = await reader.get_csv_content(
                        f"{settings.BASE_DIR}/media/{new_file}"
                    )
                elif _format == "txt":
                    questions = await reader.get_txt_content(
                        f"{settings.BASE_DIR}/media/{new_file}"
                    )

                if not questions:
                    message_to_user = texts['file_no_questions'][user.language]
                    await message.answer(message_to_user)
                else:
                    os.remove(f"{settings.BASE_DIR}/media/{new_file}")
                    message_to_user = texts['test_duration'][user.language]

                    await state.update_data(test_questions=questions)
                    await message.answer(message_to_user, reply_markup=await reply.duration_markup(
                        texts, user.language
                    ))
                    await state.set_state(NewQuizState.duration)

            except Exception as e:
                print(e)
                message_to_user = texts['problem_with_file'][user.language]
                await message.answer(
                    message_to_user,
                    reply_markup=await inline.generate_markup({"🔙": "back"})
                )

        else:
            message_to_user = texts['no_file_format'][user.language]
            await message.answer(
                message_to_user,
                reply_markup=await inline.generate_markup({"🔙": "back"})
            )

    else:
        message_answer_text = texts['no_file'][user.language]
        await bot.delete_message(message.from_user.id, message.message_id)
        await message.answer(message_answer_text, reply_markup=await inline.generate_markup({"🔙": "back"}))


@dp_user.message(NewQuizState.quantity)
async def new_quiz_quantity(message: types.Message, bot: Bot, state: FSMContext):
    texts = await get_texts(state)
    user = await get_user(state, message.from_user.id)

    if message.content_type == ContentType.TEXT:
        if message.text.isdigit():
            quantity = int(message.text)
            if quantity in (20, 25, 30, 35, 40, 45, 50):
                message_to_user = texts['test_duration'][user.language]
                await state.update_data(test_quantity=quantity)
                await message.answer(message_to_user, reply_markup=await reply.duration_markup(
                    texts, user.language
                ))
                await state.set_state(NewQuizState.duration)

            else:
                message_to_user = texts['below_button'][user.language]
                await message.answer(message_to_user, reply_markup=await reply.duration_markup(
                    texts, user.language
                ))
        else:
            message_to_user = texts['below_button'][user.language]
            await message.answer(message_to_user, reply_markup=await reply.duration_markup(
                texts, user.language
            ))
    else:
        message_to_user = texts['below_button'][user.language]
        await message.answer(message_to_user, reply_markup=await reply.duration_markup(
            texts, user.language
        ))


@dp_user.message(NewQuizState.duration)
async def new_quiz_duration(message: types.Message, bot: Bot, state: FSMContext):
    texts = await get_texts(state)
    user = await get_user(state, message.from_user.id)

    if message.text == "🔙 " + texts['back'][user.language]:
        message_to_user = texts['test_file'][user.language]
        msg = await message.answer("Delete reply markup", reply_markup=types.ReplyKeyboardRemove())
        await bot.delete_message(message.chat.id, msg.message_id)
        await message.answer(message_to_user, reply_markup=await inline.generate_markup({"🔙": "back"}))
        await state.set_state(NewQuizState.file)

    elif message.text.split(" ")[0].isdigit():
        duration = int(message.text.split(" ")[0])

        if duration in [i for i in range(10, 61, 5)]:
            await state.update_data(test_duration=duration)
            await save_data(message, bot, state)
        else:
            message_to_user = texts['below_button'][user.language]
            await message.answer(message_to_user, reply_markup=await reply.duration_markup(
                texts, user.language
            ))
    else:
        message_to_user = texts['below_button'][user.language]
        await message.answer(message_to_user, reply_markup=await reply.duration_markup(
            texts, user.language
        ))


@dp_user.callback_query(NewQuizState.title, F.data == "back")
async def back(call: types.CallbackQuery, state: FSMContext):
    user = await get_user(state, call.message.chat.id)
    texts = await get_texts(state)

    message_to_user = f"🤖 {texts['menu'][user.language]} ⬇️"
    buttons = texts['main_menu_buttons'][user.language]
    await call.message.edit_text(message_to_user, reply_markup=await inline.main_menu_markup(buttons))
    await call.answer()
    await state.clear()


@dp_user.callback_query(NewQuizState.file, F.data == "back")
async def back_to_title(call: types.CallbackQuery, state: FSMContext):
    user = await get_user(state, call.message.chat.id)
    texts = await get_texts(state)

    message_to_user = texts['test_title'][user.language]
    await call.message.delete()
    await call.message.answer(message_to_user, reply_markup=await inline.generate_markup(
        {"🔙": "back"}))
    await state.set_state(NewQuizState.title)
    await call.answer()


