from typing import Union

from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, KeyboardBuilder
from django.db.models import QuerySet

from tgbot.bot.handlers.utils import username_filtering
from tgbot.bot.utils import get_texts


async def generate_markup_url(texts: dict, sizes=(1,)) -> KeyboardBuilder:
    markup = InlineKeyboardBuilder()
    for text, value in texts.items():
        markup.add(
            InlineKeyboardButton(
                text=text, url=value, switch_inline_keyboard=True
            ))
    return markup.adjust(*sizes)


async def channels_markup(channels, text=None):
    builder = InlineKeyboardBuilder()
    builder.add(*[InlineKeyboardButton(
        text=f"{text}", callback_data="check_subscription"
    )])
    markup = await generate_markup_url(
        {channel.title: f"https://t.me/{str(channel.username).replace('@', '')}" for channel in channels}
    )
    markup.attach(builder)
    return markup.as_markup()


async def languages_markup(languages, link=""):
    markup = InlineKeyboardBuilder()
    for language in languages:
        markup.add(InlineKeyboardButton(
            text=f"{language.title}", callback_data=f"lang_{language.code}_{link}"
        ))
    return markup.adjust(*(1,)).as_markup()


async def main_menu_markup(buttons: dict):
    markup = InlineKeyboardBuilder()
    markup2 = InlineKeyboardBuilder()
    markup.add(InlineKeyboardButton(
        text=f"📖 {buttons[3]}", callback_data=f"menu_{3}"))
    markup.add(InlineKeyboardButton(
        text=f"🖌 {buttons[2]}", callback_data=f"menu_{2}"))
    markup2.add(InlineKeyboardButton(
        text=f"🗞 {buttons[1]}", callback_data=f"menu_{1}"))
    markup2.add(InlineKeyboardButton(
        text=f"⚙️ {buttons[4]}", callback_data=f"menu_{4}"))
    markup.adjust(*(2,))
    markup2.adjust(*(1,))
    return markup.attach(markup2).as_markup()


async def pagination_markup(texts: dict, language: str, total_page, current_page):
    keyboard = InlineKeyboardBuilder()

    if current_page > 1:
        keyboard.add(
            InlineKeyboardButton(
                text="⬅️", callback_data=f"pagination_{current_page - 1}"
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text=f"{current_page}", callback_data=f"pagination_{current_page}"
        )
    )
    if current_page < total_page:
        keyboard.add(
            InlineKeyboardButton(text="➡️", callback_data=f"pagination_{current_page + 1}")
        )
    keyboard2 = InlineKeyboardBuilder().add(InlineKeyboardButton(
        text=texts['menu'][language], callback_data="pagination_menu"))
    return keyboard.adjust(*(3,)).attach(keyboard2).as_markup()


async def instruction_markup(buttons, sizes=(1,)):
    items = {f"📝 {buttons[1]}": buttons[1],
             f"🎬 {buttons[2]}": buttons[2],
             f"🔙 {buttons[3]}": buttons[3]}
    keyboard = InlineKeyboardBuilder()
    for key, value in items.items():
        keyboard.add(
            InlineKeyboardButton(
                text=key,
                callback_data=f"instruction_{value}"
            )
        )
    keyboard.adjust(*sizes)
    return keyboard.as_markup()


async def quiz_markup(texts, language, link, is_inline_query=False):
    start = texts['start'][language]
    start_in_group = texts['start_in_group'][language]
    share = texts['share'][language]
    keyboard = InlineKeyboardBuilder()

    start_btn = InlineKeyboardButton(
        text=start, callback_data=f"quiz__{link}"
    )

    if is_inline_query:
        start_btn = InlineKeyboardButton(
            text=start, url=f"https://t.me/FileToQuiz_bot?start={link}"
        )
    keyboard.add(
        start_btn,
        InlineKeyboardButton(
            text=start_in_group, url=f"https://t.me/FileToQuiz_bot?startgroup={link}"
        ),
        InlineKeyboardButton(
            text=share, switch_inline_query=f"share_{link}"
        )
    )

    return keyboard.adjust(*(1,)).as_markup()


async def quiz_retry_markup(texts, language, link):
    retry = texts['retry'][language]
    start_in_group = texts['start_in_group'][language]
    share = texts['share'][language]
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text=retry, callback_data=f"quiz_retry__{link}"
        ),
        InlineKeyboardButton(
            text=start_in_group, url=f"https://t.me/FileToQuiz_bot?startgroup={link}"
        ),
        InlineKeyboardButton(
            text=share, switch_inline_query=f"share_{link}"
        )
    )

    return keyboard.adjust(*(1,)).as_markup()


async def share_markup(texts, language, link):
    share = texts['share'][language]
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text=share, switch_inline_query=f"share_{link}"
        )
    )
    return keyboard.as_markup()


async def generate_markup(buttons: dict, sizes=(1,)) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for key, value in buttons.items():
        keyboard.add(
            InlineKeyboardButton(
                text=key,
                callback_data=f"{value}"
            )
        )
    return keyboard.adjust(*sizes).as_markup()


async def admin_pagination_markup(
        state: FSMContext, users: Union[list, QuerySet], total_page: int, current_page: int = 1
):
    keyboard = InlineKeyboardBuilder()
    users_keyboard = InlineKeyboardBuilder()
    extra = InlineKeyboardBuilder()

    data = await state.get_data()
    chosen_users = data.get("chosen_users", {})

    for user in users:
        username = "@" + user['username'] if user['username'] else user['first_name']
        username = username_filtering(username)
        chat_id = user['chat_id']
        _id = user['id']

        text = f"{username} ☑️" if not chosen_users.get(str(chat_id), None) else f"{username} ✅"
        users_keyboard.add(InlineKeyboardButton(text=text, callback_data=f"choose-user_{_id}_{chat_id}"))


    # pagination part
    if current_page > 1:
        keyboard.add(
            InlineKeyboardButton(
                text="⬅️", callback_data=f"{current_page - 1}"
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text=f"{current_page}", callback_data=f"{current_page}"
        )
    )
    if current_page < total_page:
        keyboard.add(
            InlineKeyboardButton(text="➡️", callback_data=f"{current_page + 1}")
        )

    keyboard = users_keyboard.adjust(*(1,)).attach(keyboard.adjust(*(3,)))
    if chosen_users:
        extra.add(InlineKeyboardButton(text=f"📂 Saqlash", callback_data="save-users"))
    else:
        extra.add(InlineKeyboardButton(text=f"✅ Barcha", callback_data="save-users_all"))
    keyboard.attach(extra)

    return keyboard.as_markup()
