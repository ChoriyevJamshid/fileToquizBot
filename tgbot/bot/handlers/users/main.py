# import asyncio
# import csv
# import os
# import uuid
#
# from aiogram.types import Message
# from django.conf import settings
# from aiogram.fsm.context import FSMContext
# from asgiref.sync import sync_to_async
# from aiogram import Bot, types, Router, F
# from aiogram.filters import CommandStart, Command
#
# from tgbot.bot.keyboards import reply
# from tgbot.bot.states.main import NewQuizState
# from tgbot.bot.engine import excel
#
# from tgbot.models import Test, Question, Option, DurationChoice
# from tgbot.bot.utils import get_or_create_user
#
# dp_user = Router()
#
#
# @dp_user.message(CommandStart())
# async def start_func(message: types.Message):
#     chat_id = message.chat.id
#     first_name = message.chat.first_name
#     last_name = message.chat.last_name
#     username = message.chat.username
#     user = get_or_create_user(chat_id, first_name, last_name, username)
#
#     await message.answer("Hello")
#
#
# @dp_user.message(Command("newquiz"))
# async def create_quiz(message: types.Message, state: FSMContext):
#     chat_id = message.chat.id
#     user = get_or_create_user(chat_id)
#
#     message_answer_text = "Keling, yangi test tuzamiz. Dastlab, menga testingiz sarlavhasini (masalan, “Qobiliyatni aniqlash testi” yoki “Ayiqlar haqida 10 ta savol”) yuboring."
#
#     await message.answer(message_answer_text)
#     await state.set_state(NewQuizState.title)
#
#
# @dp_user.message(NewQuizState.title)
# async def process_title(message: types.Message, state: FSMContext):
#     chat_id = message.chat.id
#     user = get_or_create_user(chat_id)
#
#     message_answer_text = "Endi .xlsx, .txt, .csv formatda testlariz mavjud fayl yuklang!"
#     await state.update_data({"title": message.text})
#     await message.answer(message_answer_text)
#     await state.set_state(NewQuizState.file)
#
#
# @dp_user.message(NewQuizState.file)
# async def get_file(message: types.Message, state: FSMContext, bot: Bot):
#     chat_id = message.chat.id
#     user = get_or_create_user(chat_id)
#
#     if message.content_type == types.ContentType.DOCUMENT:
#         os.makedirs(f"{settings.BASE_DIR}/media", exist_ok=True)
#
#         data = await state.get_data()
#         title = data.get("title")
#
#         file_id = message.document.file_id
#         file = await bot.get_file(file_id)
#         _format = file.file_path.split(".")[-1]
#         file_name = title if title else str(uuid.uuid4())
#
#         await bot.download_file(file.file_path, f"media/{file_name}.{_format}")
#         try:
#             question_list = await excel.get_excel_content(f"{settings.BASE_DIR}/media/{file_name}.{_format}", _format)
#         except Exception as e:
#             print(e)
#             return
#         await state.update_data({"question_list": question_list})
#         message_answer_text = """
# Savollar uchun vaqt belgilang. Guruhlarda bot vaqt tugashi bilanoq keyingi savolni yuboradi.
#
# Agar savolingiz murakkab masalalarni oʻz ichiga olsa (masalan, matematika va boshqalar), uzoqroq vaqt ajratishingizni maslahat beramiz. Koʻplab oddiy testlar uchun 10-30 soniya kifoya qiladi.
# """
#         await message.answer(message_answer_text, reply_markup=reply.generate_markup(
#             DurationChoice.labels, (2,)
#         ))
#         await state.set_state(NewQuizState.duration)
#
#     else:
#         message_answer_text = "Iltimos, .xlsx, .txt, .csv formatda testlariz mavjud fayl yuklang!"
#         await message.answer(message_answer_text)
#
#
# @dp_user.message(NewQuizState.duration)
# async def process_duration(message: types.Message, state: FSMContext):
#     chat_id = message.chat.id
#     user = get_or_create_user(chat_id)
#
#     if message.text in DurationChoice.labels:
#         await state.update_data({"duration": message.text})
#         await message.answer("Testlariz nechta variantdan iboratligini kiriting.",
#                              reply_markup=reply.generate_markup(
#                                  MaxOptionChoice.labels, (3,)
#                              ))
#         await state.set_state(NewQuizState.max_option)
#     else:
#         message_answer_text = "Iltimos, pastdagi tugmalardan foydalaning!"
#         await message.answer(message_answer_text, reply_markup=reply.generate_markup(
#             DurationChoice.labels, (2,)
#         ))
#
#
# @dp_user.message(NewQuizState.max_option)
# async def process_max_option(message: types.Message, state: FSMContext, bot: Bot):
#     chat_id = message.chat.id
#     user = get_or_create_user(chat_id)
#
#     if message.text in MaxOptionChoice.labels:
#         await state.update_data({"max_option": message.text})
#         await message.answer("Ma'lumotlariz qabul qilindi", reply_markup=types.ReplyKeyboardRemove())
#         await save_quiz_to_db(message, state, bot)
#
#     else:
#         await message.answer("Testlariz nechta variantdan iboratligini kiriting. Bu juda muhim.",
#                              reply_markup=reply.generate_markup(
#                                  MaxOptionChoice.labels, (3,)
#                              ))
#
#
# async def save_quiz_to_db(message: types.Message, state: FSMContext, bot: Bot):
#     print("SAVE")
#     chat_id = message.chat.id
#     user = get_or_create_user(chat_id)
#     data = await state.get_data()
#
#     title = data.get("title")
#     question_list = data.get("question_list")
#     duration = data.get("duration").split(" ")[0]
#     max_option = data.get("max_option")
#     print(f'\nmax_option = {max_option}\n')
#
#     max_questions = len(question_list)
#     # questions = []
#     options = []
#     question = None
#     test = Test.objects.create(
#         telegram_profile=user,
#         title=title,
#         timer=duration
#     )
#     for index, value in enumerate(question_list):
#         if (index + 1) % (int(max_option) + 1) == 1:
#             question = Question.objects.create(
#                 question=value,
#                 test=test,
#             )
#         else:
#             is_correct = False
#             if index % int(max_option) == 2:
#                 is_correct = True
#             options.append(
#                 Option(option=value, question=question, is_correct=is_correct)
#             )
#     if options:
#         Option.objects.bulk_create(options)
#         await state.clear()
#
# # @dp_user.message(Command("poll"))
# # async def quiz(message: types.Message, bot: Bot):
# #     chat_id = message.chat.id
# #
# #     await message.answer_poll(
# #         question="What is your name",
# #         options=["Jamshid", "Jamshid2", "Jamshid3"],
# #         type="quiz",
# #         correct_option_id=2,
# #         open_period=60,
# #         is_anonymous=False,
# #         protect_content=True
# #     )
# #
# #
# # @dp_user.poll_answer()
# # async def get_user_answer(poll: types.PollAnswer, bot: Bot):
# #     print(poll)
# #     print(poll.voter_chat)
# #     print(poll.user)
# #     print(poll.poll_id)
