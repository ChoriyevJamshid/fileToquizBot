from aiogram.types import SwitchInlineQueryChosenChat
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, KeyboardBuilder

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


async def languages_markup(languages):
    markup = InlineKeyboardBuilder()
    for language in languages:
        markup.add(InlineKeyboardButton(
            text=f"{language.title}", callback_data=f"lang_{language.code}"
        ))
    return markup.adjust(*(1,)).as_markup()


async def main_menu_markup(buttons: dict):
    markup = InlineKeyboardBuilder()
    markup.add(InlineKeyboardButton(
        text=f"🗞 {buttons[1]}", callback_data=f"menu_{1}"))
    markup.add(InlineKeyboardButton(
        text=f"🖌 {buttons[2]}", callback_data=f"menu_{2}"))
    markup.add(InlineKeyboardButton(
        text=f"📖 {buttons[3]}", callback_data=f"menu_{3}"))
    markup.add(InlineKeyboardButton(
        text=f"⚙️ {buttons[4]}", callback_data=f"menu_{4}"))
    return markup.adjust(*(2,)).as_markup()


# async def user_tests_markup(buttons, state):
#     data = await state.get_data()
#     current_page = data.get("current_page", 1)
#     number_of_tests = len(buttons)
#     in_page = 4
#     total_page = number_of_tests // in_page + 1 if number_of_tests % in_page else number_of_tests // in_page
#     markup = InlineKeyboardBuilder()
#     to = in_page * current_page if in_page * current_page < number_of_tests else number_of_tests
#     for button in buttons[(current_page - 1) * in_page: to]:
#         markup.add(
#             InlineKeyboardButton(
#                 text=f"{button.title}", callback_data=f"test_{button.id}"
#             )
#         )
#     markup = markup.adjust(*(1,))
#     if number_of_tests > in_page:
#         pagination_builder = InlineKeyboardBuilder()
#         if current_page > 1:
#             pagination_builder.add(
#                 InlineKeyboardButton(
#                     text="⬅️", callback_data=f"pagination_{current_page - 1}"
#                 )
#             )
#         pagination_builder.add(
#             InlineKeyboardButton(
#                 text=f"{current_page}", callback_data=f"pagination_{current_page}"
#             )
#         )
#         if current_page < total_page:
#             pagination_builder.add(
#                 InlineKeyboardButton(text="➡️", callback_data=f"pagination_{current_page + 1}")
#             )
#         markup.attach(pagination_builder.adjust(*(3,)))
#     markup.attach(InlineKeyboardBuilder().add(
#         InlineKeyboardButton(text="🔙", callback_data="pagination_back")
#     ))
#     await state.update_data({"current_page": current_page})
#     return markup.as_markup()


async def pagination_markup(total_page, current_page):
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

    return keyboard.adjust(*(3,)).as_markup()


# async def test_markup(test_id, part, test_uuid, user, state):
#     texts = await get_texts(state)
#     builder = InlineKeyboardBuilder()
#     start_btn = InlineKeyboardButton(
#         text=texts['start'][user.language],
#         callback_data=f"testing_{test_uuid}_{test_id}"
#     )
#     share_btn = InlineKeyboardButton(
#         text=texts['share'][user.language],
#         # switch_inline_query=f"share_{test_uuid}_{test_id}"
#         switch_inline_query=f"quiz-{test_id}-{part}-{test_uuid}"
#     )
#     builder.add(start_btn, share_btn)
#     return builder.adjust(*(2,)).as_markup()


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


async def quiz_markup(texts, language, link):
    start = texts['start'][language]
    start_in_group = texts['start_in_group'][language]
    share = texts['share'][language]
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text=start, callback_data=f"quiz__{link}"
        ),
        InlineKeyboardButton(
            text=start_in_group, url=f"https://t.me/FileToQuiz_bot?startgroup={link}"
        ),
        InlineKeyboardButton(
            text=share, switch_inline_query=f"share_{link}"
        )
    )

    return keyboard.adjust(*(1,)).as_markup()


async def generate_markup(buttons, sizes=(1,)):
    keyboard = InlineKeyboardBuilder()
    for key, value in buttons.items():
        keyboard.add(
            InlineKeyboardButton(
                text=key,
                callback_data=f"{value}"
            )
        )
    return keyboard.adjust(*sizes).as_markup()

