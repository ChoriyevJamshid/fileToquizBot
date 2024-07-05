import random

from django.conf import settings
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from aiogram import Bot, types, Router, F
from aiogram.filters import CommandStart, Command

from tgbot.bot.handlers.utils import generate_random_string
from tgbot.bot.keyboards import inline, reply
from tgbot.bot.states.main import NewQuizState, InstructionState
from tgbot.bot.utils import check_subscription, get_channels, get_user, get_texts, get_languages
from tgbot.models import Quiz, QuizPart

from tgbot.bot.filters.filter import ChatTypeFilter

dp_user = Router()
dp_user.message.filter(ChatTypeFilter(["private"]))


@dp_user.message(CommandStart())
async def start(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()

    chat_id = message.chat.id
    user = await get_user(state, chat_id,
                          message.from_user.first_name,
                          message.from_user.last_name,
                          message.from_user.username)
    lang = user.language
    if lang is None:
        message_to_user = "🌐 Til tanlash uchun quidagil tugmalardan foydalaning. 👇"
        languages = await get_languages(state)
        await message.answer(message_to_user, reply_markup=await inline.languages_markup(languages))
    else:
        channels = data.get("channels")
        texts = await get_texts(state)

        if not channels:
            channels = get_channels()
        status = await check_subscription(bot, chat_id, channels)

        if not status:
            message_to_user = f"🔔 {texts['subscribe'][user.language]}"
            await message.answer(
                message_to_user,
                reply_markup=await inline.channels_markup(
                    channels,
                    text=f"✅ {texts['check_subscribe'][user.language]}"
                ))
        else:
            message_to_user = f"🤖 {texts['menu'][user.language]} ⬇️"
            buttons = texts['main_menu_buttons'][user.language]
            await message.answer(message_to_user, reply_markup=await inline.main_menu_markup(buttons))


@dp_user.callback_query(F.data.startswith("lang"))
async def change_language(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    chat_id = call.message.chat.id
    data = await state.get_data()

    code = call.data.split("_")[-1]

    user = await get_user(state, chat_id)
    user.language = code
    user.save(update_fields=["language"])

    channels = get_channels()
    status = await check_subscription(bot, chat_id, channels)
    texts = await get_texts(state)
    if not status:
        message_to_user = f"🔔 {texts['subscribe'][user.language]}"
        await call.message.answer(message_to_user,
                                  reply_markup=await inline.channels_markup(
                                      channels,
                                      text=f"✅ {texts['check_subscribe'][user.language]}"
                                  ))
        await state.update_data({"channels": channels})
    else:
        message_to_user = f"🤖 {texts['menu'][user.language]} ⬇️"
        buttons = texts['main_menu_buttons'][user.language]
        await call.message.edit_text(message_to_user, reply_markup=await inline.main_menu_markup(buttons))
    await call.answer()


@dp_user.callback_query(F.data.startswith("check"))
async def process_check_subscribe(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    user = await get_user(state, call.from_user.id)
    texts = await get_texts(state)
    if call.data.split("_")[1] == "subscription":
        channels = data.get("channels")
        if not channels:
            channels = get_channels()
        status = await check_subscription(bot, call.message.chat.id, channels)
        if status:
            message_to_user = texts['menu'][user.language]

            await call.message.answer(message_to_user, reply_markup=None)
        else:
            text = texts['not_subscribe'][user.language]
            await call.answer(text, show_alert=True)
    return await call.answer()


@dp_user.callback_query(F.data.startswith("menu"))
async def process_menu(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    user = await get_user(state, call.from_user.id)
    texts = await get_texts(state)

    if call.data.split("_")[-1] == "1":
        buttons = texts['instruction_buttons'][user.language]
        message_to_user = f"🗞 {texts['instruction'][user.language]} 👇"
        await call.message.edit_text(
            message_to_user, reply_markup=await inline.instruction_markup(buttons, (2,))
        )

    if call.data.split("_")[-1] == "2":
        if user.is_verified:
            message_to_user = texts['test_title'][user.language]
            await call.message.answer(message_to_user, reply_markup=None)
            await state.set_state(NewQuizState.title)
        else:
            message_to_user = texts['no_verified'][user.language]
            await call.message.answer(message_to_user, reply_markup=None)

    if call.data.split("_")[-1] == "3":
        quizzes = Quiz.objects.filter(user_id=user.id)
        if quizzes.exists():

            message_to_user = ""
            markup = None

            PAGINATE_BY = settings.PAGINATE_BY
            current_page = user.data.get("current_page", 1)

            total_page = len(quizzes) // PAGINATE_BY if len(quizzes) % PAGINATE_BY == 0 else len(
                quizzes) // PAGINATE_BY + 1
            to_number = len(quizzes) if current_page * PAGINATE_BY > len(quizzes) else current_page * PAGINATE_BY

            for i in range((current_page - 1) * PAGINATE_BY, to_number):
                message_to_user += f"<b>{i + 1}</b>. <i>{quizzes[i].title}</i> 👉 /{quizzes[i].link}\n"
            message_to_user += f"\n{texts['menu'][user.language]} 👉 /start"

            if total_page > 1:
                markup = await inline.pagination_markup(total_page, current_page)

            user.data['current_page'] = current_page
            user.data['total_page'] = total_page
            user.save(update_fields=["data"])

            await call.message.answer(message_to_user, reply_markup=markup)

        else:
            message_to_user = texts['no_quizzes'][user.language]
            await call.message.answer(message_to_user, reply_markup=None)

    if call.data.split("_")[-1] == "4":
        message_to_user = f"🌐 {texts['change_language'][user.language]} 👇"
        languages = await get_languages(state)
        await call.message.edit_text(message_to_user, reply_markup=await inline.languages_markup(languages))

    await call.answer()


@dp_user.callback_query(F.data.startswith("pagination"))
async def process_pagination(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    user = await get_user(state, call.from_user.id)
    texts = await get_texts(state)

    page_number = int(call.data.split("_")[-1])
    current_page = int(user.data.get("current_page", 1))
    total_page = int(user.data.get("total_page"))

    if page_number != current_page:
        current_page = page_number
        quizzes = Quiz.objects.filter(user_id=user.id)
        PAGINATE_BY = settings.PAGINATE_BY
        to_number = len(quizzes) if current_page * PAGINATE_BY > len(quizzes) else current_page * PAGINATE_BY

        message_to_user = ""
        for i in range((current_page - 1) * PAGINATE_BY, to_number):
            message_to_user += f"<b>{i + 1}</b>. <i>{quizzes[i].title}</i> 👉 /{quizzes[i].link}\n"
        message_to_user += f"\n{texts['menu'][user.language]} 👉 /start"

        user.data['current_page'] = current_page
        user.data['total_page'] = total_page
        user.save(update_fields=["data"])

        await call.message.edit_text(
            message_to_user,
            reply_markup=await inline.pagination_markup(total_page, current_page))

