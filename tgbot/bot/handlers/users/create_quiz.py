import asyncio
import csv
import os

from aiogram import Bot, types
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from django.conf import settings

from tgbot.bot.keyboards import reply
from tgbot.bot.states.main import NewQuizState
from tgbot.bot.engine import excel
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
    # print('\ncreated new quiz part\n')
    # print(quiz_part)
    quiz_part.data = dict()
    quiz_part.data['questions'] = quiz_part_list
    quiz_part.save(update_fields=['data'])


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

    except Exception:
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
                question_data['question'] = value
                question_data['options'] = []
                is_correct = True
            else:
                question_data['options'].append(value)
                if is_correct:
                    question_data['correct_option'] = value
                    is_correct = False

                if index % 5 == 0:
                    quiz_part_list.append(question_data)
                    if ques_count % 25 == 0:
                        create_quiz_part(quiz, ques_count, quiz_part_list)
                        quiz_part_list = list()
                        # while True:
                        #     new_link = generate_random_string()
                        #     if not QuizPart.objects.filter(link=new_link).exists():
                        #         break
                        #
                        # quiz_part = QuizPart.objects.create(
                        #     quiz_id=quiz.id,
                        #     link=new_link,
                        #     from_number=ques_count - 24,
                        #     to_number=ques_count,
                        # )
                        # quiz_part.data = dict()
                        # quiz_part.data['questions'] = quiz_part_list
                        # quiz_part.save(update_fields=['data'])

        if 0 < len(quiz_part_list) < 25:
            create_quiz_part(quiz, ques_count, quiz_part_list)
            # while True:
            #     new_link = generate_random_string()
            #     if not QuizPart.objects.filter(link=new_link).exists():
            #         break
            # quiz_part = QuizPart.objects.create(
            #     quiz_id=quiz.id,
            #     link=new_link,
            #     from_number=ques_count - 24,
            #     to_number=ques_count,
            # )
            # quiz_part.data = dict()
            # quiz_part.data['questions'] = quiz_part_list
            # quiz_part.save(update_fields=['data'])

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
                texts['quiz_title_unique'][user.language]
            )
        else:
            await state.update_data(test_title=message.text)

            message_to_user = texts['test_file'][user.language]
            await message.answer(message_to_user)
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

        if _format in ('xls', 'xlsx'):
            try:
                questions = await excel.get_excel_content(
                    f"{settings.BASE_DIR}/media/{new_file}",
                    _format=_format
                )
                # print(questions)
                if not questions:
                    message_to_user = texts['file_no_questions'][user.language]
                    await message.answer(message_to_user)
                else:
                    # print('\nOK\n')
                    os.remove(f"{settings.BASE_DIR}/media/{new_file}")

                    # message_to_user = texts['test_quantity'][user.language]
                    # await state.update_data(test_questions=questions)
                    # await message.answer(message_to_user, reply_markup=await reply.quantity_markup())
                    # await state.set_state(NewQuizState.quantity)
                    message_to_user = texts['test_duration'][user.language]
                    # await state.update_data(test_quantity=quantity)
                    await state.update_data(test_questions=questions)
                    await message.answer(message_to_user, reply_markup=await reply.duration_markup())
                    await state.set_state(NewQuizState.duration)

            except Exception as e:
                print(e)
                message_to_user = texts['problem_with_file'][user.language]
                await message.answer(message_to_user)

        else:
            message_to_user = texts['no_file_format'][user.language]
            await message.answer(message_to_user)

    else:
        message_answer_text = texts['no_file'][user.language]
        await bot.delete_message(message.from_user.id, message.message_id)
        await message.answer(message_answer_text)


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
                await message.answer(message_to_user, reply_markup=await reply.duration_markup())
                await state.set_state(NewQuizState.duration)

            else:
                message_to_user = texts['below_button'][user.language]
                await message.answer(message_to_user, reply_markup=await reply.duration_markup())
        else:
            message_to_user = texts['below_button'][user.language]
            await message.answer(message_to_user, reply_markup=await reply.duration_markup())
    else:
        message_to_user = texts['below_button'][user.language]
        await message.answer(message_to_user, reply_markup=await reply.duration_markup())


@dp_user.message(NewQuizState.duration)
async def new_quiz_duration(message: types.Message, bot: Bot, state: FSMContext):
    texts = await get_texts(state)
    user = await get_user(state, message.from_user.id)
    if message.text.isdigit():
        duration = int(message.text)

        if duration in [i for i in range(10, 61, 5)]:
            await state.update_data(test_duration=duration)

            # message_to_user = texts['test_options_number'][user.language]
            # await message.answer(message_to_user, reply_markup=await reply.generate_markup(
            #     (3, 4, 5), (1,)
            # ))
            # await state.set_state(NewQuizState.max_option)
            await save_data(message, bot, state)
        else:
            message_to_user = texts['below_button'][user.language]
            await message.answer(message_to_user, reply_markup=await reply.duration_markup())
    else:
        message_to_user = texts['below_button'][user.language]
        await message.answer(message_to_user, reply_markup=await reply.duration_markup())

# @dp_user.message(NewQuizState.max_option)
# async def new_quiz_max_option(message: types.Message, bot: Bot, state: FSMContext):
#     texts = await get_texts(state)
#     user = await get_user(state, message.from_user.id)
#
#     if message.text.isdigit():
#         max_option = int(message.text)
#         if max_option in (3, 4, 5):
#             await state.update_data(test_max_option=max_option)
#             message_to_user = texts['go_to_main'][user.language]
#             await message.answer(message_to_user, reply_markup=types.ReplyKeyboardRemove())
#             await save_data(message, bot, state)
#
#         else:
#             message_to_user = texts['below_button'][user.language]
#             await message.answer(message_to_user, reply_markup=await reply.generate_markup(
#                 (3, 4, 5), (1,)
#             ))
#     else:
#         message_to_user = texts['below_button'][user.language]
#         await message.answer(message_to_user, reply_markup=await reply.generate_markup(
#             (3, 4, 5), (1,)
#         ))
