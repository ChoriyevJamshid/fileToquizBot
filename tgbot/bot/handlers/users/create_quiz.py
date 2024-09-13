import os

from aiogram import Bot, types, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from django.conf import settings
from django.templatetags.i18n import language

from tgbot.bot.keyboards import reply, inline
from tgbot.bot.states.main import NewQuizState
from tgbot.bot import engine
from tgbot.bot.utils import get_user

from tgbot.models import Quiz, QuizPart
from tgbot.bot.handlers.users import dp_user
from tgbot.bot.handlers.utils import generate_random_string


def create_quiz_part(quiz_id: int, question_list: list, from_number: int, to_number: int):
    while True:
        new_link = generate_random_string(length=12)
        if not QuizPart.objects.filter(link=new_link).exists():
            break

    quiz_part = QuizPart.objects.create(
        quiz_id=quiz_id,
        link=new_link,
        from_number=from_number,
        to_number=to_number,
    )
    quiz_part.data['questions'] = question_list
    quiz_part.save()


async def save_data(message: types.Message, state: FSMContext, texts: dict):
    data = await state.get_data()
    user = await get_user(message.chat)
    language = user.language if user.language else 'uz'
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

    if not quiz:
        return await state.clear()

    question_list = data.get('questions')
    quantity = len(question_list)
    cycles = quantity // 25 if not quantity % 25 else quantity // 25 + 1

    for i in range(cycles):
        if i + 1 != cycles:
            to = (i + 1) * 25
        else:
            to = quantity
        questions = question_list[i * 25: to]
        create_quiz_part(quiz.id, questions, (i * 25 + 1), to)
    quiz.quantity = quantity
    quiz.save(update_fields=['quantity'])
    user.quiz_number -= 1
    user.save(update_fields=['quiz_number'])
    message_to_user = texts['test_created'][language]
    await message.answer(message_to_user, reply_markup=types.ReplyKeyboardRemove())
    if user.quiz_number > 0:
        await message.answer(str(texts['limits'][language]).replace('__x__', f'<b>{user.quiz_number}</b>'))
    else:
        await message.answer(
            texts['no_limits'][language],
            reply_markup=await inline.share_friends_markup(texts['share_friends'][language])
        )
    await state.clear()


@dp_user.message(NewQuizState.title)
async def new_quiz_title(message: types.Message, state: FSMContext, texts: dict):
    user = await get_user(message.chat)
    language = user.language if user.language else 'uz'
    if message.content_type == ContentType.TEXT:

        if message.text.startswith("🔙"):
            message_to_user = f"🤖 {texts['menu'][user.language]} ⬇️"
            buttons = texts['main_menu_buttons'][user.language]
            await message.answer('...', reply_markup=await reply.remove_markup())
            await message.answer(message_to_user, reply_markup=await inline.main_menu_markup(buttons, texts, language))
            return await state.clear()

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
async def new_quiz_file(message: types.Message, bot: Bot, state: FSMContext, texts: dict):
    user = await get_user(message.chat)

    if message.content_type == ContentType.DOCUMENT:
        os.makedirs(f"{settings.BASE_DIR}/media", exist_ok=True)

        file_id = message.document.file_id
        file = await bot.get_file(file_id)
        _format = file.file_path.split('.')[-1]
        new_file = f"{file.file_id}.{_format}"
        await bot.download_file(file.file_path, f"media/{new_file}")

        if _format in ('xls', 'xlsx', 'docx', 'csv', 'txt'):
            try:
                questions = None
                if _format in ('xls', 'xlsx'):
                    questions = await engine.get_excel_content(
                        f"{settings.BASE_DIR}/media/{new_file}",
                        _format=_format
                    )
                elif _format == 'docx':
                    questions = await engine.get_docx_content(
                        f"{settings.BASE_DIR}/media/{new_file}"
                    )
                elif _format == "csv":
                    questions = await engine.get_csv_content(
                        f"{settings.BASE_DIR}/media/{new_file}"
                    )
                elif _format == "txt":
                    questions = await engine.get_txt_content(
                        f"{settings.BASE_DIR}/media/{new_file}"
                    )
                elif _format == "pdf":
                    questions = await engine.get_pdf_content(
                        f"{settings.BASE_DIR}/media/{new_file}"
                    )

                if not questions:
                    message_to_user = texts['file_no_questions'][user.language]
                    await message.answer(message_to_user)
                else:
                    os.remove(f"{settings.BASE_DIR}/media/{new_file}")
                    message_to_user = texts['test_duration'][user.language]

                    await state.update_data(questions=questions)
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
            await message.answer(message_to_user)

    else:
        message_answer_text = texts['no_file'][user.language]
        await bot.delete_message(message.from_user.id, message.message_id)
        await message.answer(message_answer_text)


@dp_user.message(NewQuizState.quantity)
async def new_quiz_quantity(message: types.Message, state: FSMContext, texts: dict):
    user = await get_user(message.chat)

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
async def new_quiz_duration(message: types.Message, state: FSMContext, texts: dict):
    user = await get_user(message.chat)

    if message.text == "🔙 " + texts['back'][user.language]:
        message_to_user = texts['test_file'][user.language]
        msg = await message.answer("Delete reply markup", reply_markup=types.ReplyKeyboardRemove())
        await message.bot.delete_message(message.chat.id, msg.message_id)
        await message.answer(message_to_user)
        await state.set_state(NewQuizState.file)

    elif message.text.split(" ")[0].isdigit():
        duration = int(message.text.split(" ")[0])

        if duration in (25, 30, 35, 40, 45, 60, 90, 120, 150):
            await state.update_data(test_duration=duration)
            await save_data(message, state, texts)
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
async def back(call: types.CallbackQuery, state: FSMContext, texts: dict):
    user = await get_user(call.from_user)

    message_to_user = f"🤖 {texts['menu'][user.language]} ⬇️"
    buttons = texts['main_menu_buttons'][user.language]
    await call.message.edit_text(message_to_user, reply_markup=await inline.main_menu_markup(buttons))
    await call.answer()
    await state.clear()


@dp_user.callback_query(NewQuizState.file, F.data == "back")
async def back_to_title(call: types.CallbackQuery, state: FSMContext, texts: dict):
    user = await get_user(call.from_user)

    message_to_user = texts['test_title'][user.language]
    await call.message.delete()
    await call.message.answer(message_to_user)
    await state.set_state(NewQuizState.title)
    await call.answer()
