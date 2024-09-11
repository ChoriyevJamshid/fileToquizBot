from django.conf import settings
from aiogram.fsm.context import FSMContext
from aiogram import types, Router, F
from aiogram.filters import CommandStart

from tgbot.bot.keyboards import inline, reply
from tgbot.bot.states.main import NewQuizState
from tgbot.bot.utils import check_subscription, get_channels, get_user, get_texts, get_languages
from tgbot.bot import utils
from tgbot.models import Quiz, QuizPart, TelegramProfile

from tgbot.bot.filters import filter

dp_user = Router()
dp_user.message.filter(filter.ChatTypeFilter(["private"]))
dp_user.message.filter(filter.UserActiveQuizFilter())
dp_user.poll_answer.filter(filter.PollAnswerFilter())


async def send_quiz(message: types.Message, user: TelegramProfile, texts: dict, link: str | None = None) -> None:
    function = message.edit_text
    if not link:
        link = message.text.split(" ")[-1]
        function = message.answer

    quiz_part = QuizPart.objects.filter(link=link)
    if quiz_part.exists():
        quiz: QuizPart = quiz_part.first()
        ques_text = texts['questions'][user.language]
        timer_text = texts['seconds'][user.language]
        message_to_user = f"""
    [{quiz.from_number} - {quiz.to_number}] {quiz.quiz.title}
🖋 {quiz.to_number - quiz.from_number + 1} {ques_text} | ⏱ {quiz.quiz.timer}-{timer_text}

{str(texts['stop_text'][user.language])}
    """
        await function(
            message_to_user,
            reply_markup=await inline.quiz_markup(texts, user.language, link)
        )


async def get_invite_user(inviter_chat_id: int, user: TelegramProfile):
    inviter_user = await utils.get_user_by_unique_field(**{"chat_id": inviter_chat_id})
    if user != inviter_user:
        inviter_user.quiz_number += 1
        inviter_user.save(update_fields=['quiz_number'])


@dp_user.message(CommandStart())
async def start(message: types.Message, state: FSMContext, texts: dict):
    await state.clear()
    user = await get_user(message.chat, message.text)
    lang = user.language
    text_data = message.text.split(" ")
    link = None
    if len(text_data) > 1:
        if text_data[-1].isdigit():
            pass
        else:
            link = text_data[-1]

    if lang is None:
        message_to_user = "🌐 Til tanlash uchun quidagil tugmalardan foydalaning. 👇"
        languages = await get_languages(state)
        link = link if link else ""
        return await message.answer(message_to_user, reply_markup=await inline.languages_markup(languages, link))

    channels = get_channels()
    status = await check_subscription(message.bot, user.chat_id, channels)

    if not status:
        message_to_user = f"🔔 {texts['subscribe'][user.language]}"

        return await message.answer(
            message_to_user,
            reply_markup=await inline.channels_markup(
                channels,
                text=f"✅ {texts['check_subscribe'][user.language]}",
            ))

    if link:
        return await send_quiz(message, user, texts)

    message_to_user = f"🤖 {texts['menu'][user.language]} ⬇️"
    buttons = texts['main_menu_buttons'][user.language]
    await message.answer(message_to_user, reply_markup=await inline.main_menu_markup(
        buttons, texts, lang))


@dp_user.callback_query(F.data.startswith("lang"))
async def change_language(call: types.CallbackQuery, state: FSMContext, texts: dict):
    print('change_language\n')
    _, code, link = call.data.split("_")
    print(repr(call.data))
    print(_)
    print(code)
    print(link)
    user = await get_user(call.from_user)
    user.language = code
    user.save(update_fields=["language"])

    channels = get_channels()
    status = await check_subscription(call.bot, user.chat_id, channels)

    if not status:
        print('Not status')
        message_to_user = f"🔔 {texts['subscribe'][user.language]}"
        await call.message.answer(message_to_user,
                                  reply_markup=await inline.channels_markup(
                                      channels,
                                      text=f"✅ {texts['check_subscribe'][user.language]}"
                                  ))
        await state.update_data({"channels": channels})
    else:
        print('Yes status')
        if not link:
            print('No link')
            message_to_user = f"🤖 {texts['menu'][user.language]} ⬇️"
            buttons = texts['main_menu_buttons'][user.language]
            await call.message.edit_text(message_to_user, reply_markup=await inline.main_menu_markup(
                buttons, texts, user.language))
        else:
            print('Yes link')
            await send_quiz(call.message, user, texts, link)
    await call.answer()


@dp_user.callback_query(F.data.startswith("check"))
async def process_check_subscribe(call: types.CallbackQuery, state: FSMContext, texts: dict):
    data = await state.get_data()
    user = await get_user(state)
    language = user.language if user.language else 'uz'
    texts = await get_texts(state)
    if call.data.split("_")[1] == "subscription":
        channels = data.get("channels")
        if not channels:
            channels = get_channels()
        status = await check_subscription(call.bot, call.message.chat.id, channels)
        if status:
            message_to_user = f"🤖 {texts['menu'][user.language]} ⬇️"
            buttons = texts['main_menu_buttons'][user.language]
            await call.message.answer(message_to_user, reply_markup=await inline.main_menu_markup(
                buttons, texts, language))
        else:
            text = texts['not_subscribe'][user.language]
            await call.answer(text, show_alert=True)
    return await call.answer()


@dp_user.callback_query(F.data.startswith("menu"))
async def process_menu(call: types.CallbackQuery, state: FSMContext, texts: dict):
    user = await get_user(call.from_user)

    language = user.language
    if not language:
        language = 'uz'

    if call.data.split("_")[-1] == "1":
        buttons = texts['instruction_buttons'][user.language]
        message_to_user = (f"🗞 <b>{texts['instruction'][user.language]}.</b>\n"
                           f"{texts['instruction_text'][user.language]}")
        await call.message.edit_text(
            message_to_user, reply_markup=await inline.instruction_markup(buttons, (2,))
        )

    if call.data.split("_")[-1] == "2":
        if not user.is_verified:
            message_to_user = texts['no_verified'][user.language]
            return await call.answer(message_to_user)

        if user.quiz_number <= 0:
            message_to_user = texts['no_limits'][user.language]
            return await call.message.answer(
                message_to_user,
                reply_markup=await inline.share_friends_markup(
                    texts['share_friends'][language]
                )
            )

        message_to_user = texts['test_title'][user.language]
        await call.message.delete_reply_markup()
        await call.message.answer(message_to_user, reply_markup=await reply.generate_markup(
            {}, (1,), texts, language
        ))
        return await state.set_state(NewQuizState.title)

    if call.data.split("_")[-1] == "3":
        quizzes = Quiz.objects.filter(user_id=user.id)

        if quizzes.exists():

            message_to_user = f'<b>📃 {texts["test_list"][language]}\n\n</b>'
            markup = None

            PAGINATE_BY = settings.PAGINATE_BY
            current_page = user.data.get("current_page", 1)

            total_page = len(quizzes) // PAGINATE_BY if len(quizzes) % PAGINATE_BY == 0 else len(
                quizzes) // PAGINATE_BY + 1
            to_number = len(quizzes) if current_page * PAGINATE_BY > len(quizzes) else current_page * PAGINATE_BY

            for i in range((current_page - 1) * PAGINATE_BY, to_number):
                message_to_user += f"<b>{i + 1}</b>. <i>{quizzes[i].title}</i> 👉 /{quizzes[i].link}\n"

            if total_page > 1:
                markup = await inline.pagination_markup(texts, language, total_page, current_page)

            user.data['current_page'] = current_page
            user.data['total_page'] = total_page
            user.save(update_fields=["data"])

            return await call.message.edit_text(message_to_user, reply_markup=markup)

        message_to_user = texts['no_quizzes'][user.language]
        await call.message.answer(message_to_user, reply_markup=None)

    if call.data.split("_")[-1] == "4":
        message_to_user = f"🌐 {texts['change_language'][user.language]} 👇"
        languages = await get_languages(state)
        await call.message.edit_text(message_to_user, reply_markup=await inline.languages_markup(languages))

    await call.answer()


@dp_user.callback_query(F.data.startswith("pagination"))
async def process_pagination(call: types.CallbackQuery, state: FSMContext, texts: dict):
    user = await get_user(call.from_user)

    language = user.language
    if not language:
        language = 'uz'

    page_number = call.data.split("_")[-1]
    current_page = int(user.data.get("current_page", 1))
    total_page = int(user.data.get("total_page"))

    if page_number == "menu":
        message_to_user = f"🤖 {texts['menu'][user.language]} ⬇️"
        buttons = texts['main_menu_buttons'][user.language]
        return await call.message.edit_text(message_to_user, reply_markup=await inline.main_menu_markup(
            buttons, texts, language))

    page_number = int(page_number)

    if page_number != current_page:
        current_page = page_number
        quizzes = Quiz.objects.filter(user_id=user.id)
        PAGINATE_BY = settings.PAGINATE_BY
        to_number = len(quizzes) if current_page * PAGINATE_BY > len(quizzes) else current_page * PAGINATE_BY

        message_to_user = ""
        for i in range((current_page - 1) * PAGINATE_BY, to_number):
            message_to_user += f"<b>{i + 1}</b>. <i>{quizzes[i].title}</i> 👉 /{quizzes[i].link}\n"

        user.data['current_page'] = current_page
        user.data['total_page'] = total_page
        user.save(update_fields=["data"])

        await call.message.edit_text(
            message_to_user,
            reply_markup=await inline.pagination_markup(texts, language, total_page, current_page))

    await call.answer()
