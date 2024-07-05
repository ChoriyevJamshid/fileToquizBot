from aiogram import Bot, types, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from django.conf import settings

from tgbot.bot.handlers.users import dp_user
from tgbot.bot.keyboards import inline
from tgbot.bot.states.main import InstructionState
from tgbot.bot.utils import get_texts, get_user

from tgbot.models import Data


# @dp_user.message(InstructionState.instruction)
# async def instruction(message: types.Message, state: FSMContext, bot: Bot):
#     user = await get_user(state, message.chat.id)
#     texts = await get_texts(state)
#     buttons = texts['instruction_buttons'][user.language]
#
#     data = Data.get_solo()
#     instruction_data = data.data['instruction']
#     if message.text == f"📝 {buttons[1]}":
#         file_id = instruction_data.get('photo', None)
#         message_to_user = f"📝 {texts['text_instruction'][user.language]} 😔"
#         if file_id:
#             message_to_user = texts['instruction_text'][user.language]
#             await message.answer_photo(
#                 photo=file_id,
#                 caption=message_to_user,
#             )
#         else:
#             await message.answer(message_to_user)
#
#     elif message.text == f"🎬 {buttons[2]}":
#         message_to_user = f"🎬 {texts['video_instruction'][user.language]} 😔"
#         video = instruction_data.get('video', None)
#         if video:
#             await message.answer_video(
#                 video=video,
#             )
#         else:
#             await message.answer(message_to_user)
#
#     elif message.text == f"🔙 {buttons[3]}":
#         message_to_user = f"🤖 {texts['menu'][user.language]} ⬇️"
#         buttons = texts['main_menu_buttons'][user.language]
#         await message
#         await message.edit_text(message_to_user, reply_markup=await inline.main_menu_markup(buttons))
#         await state.clear()
#
#     else:
#         await message.answer(f"🤖 {texts['below_button'][user.language]} 👇")


@dp_user.callback_query(F.data.startswith("instruction"))
async def instruction_callback(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    user = await get_user(state, call.message.chat.id)
    texts = await get_texts(state)
    buttons = texts['instruction_buttons'][user.language]

    data = Data.get_solo()
    instruction_data = data.data['instruction']

    call_data = call.data.split("_")[-1]

    if not user.is_verified:
        user.is_verified = True
        user.save(update_fields=['is_verified'])

    if call_data == buttons[1]:
        file_id = instruction_data.get('photo', None)
        message_to_user = f"📝 {texts['text_instruction'][user.language]} 😔\n\n👉 /start"
        if file_id:
            message_to_user = f"{texts['instruction_text'][user.language]}\n\n👉 /start"
            await call.message.answer_photo(
                photo=file_id,
            )
            await call.message.answer(message_to_user)
        else:
            await call.message.answer(message_to_user)

    elif call_data == buttons[2]:
        message_to_user = f"🎬 {texts['video_instruction'][user.language]} 😔\n\n👉 /start"
        video = instruction_data.get('video', None)
        if video:
            await call.message.answer_video(
                video=video,
            )
        else:
            await call.message.answer(message_to_user)

    elif call_data == buttons[3]:
        message_to_user = f"🤖 {texts['menu'][user.language]} ⬇️"
        buttons = texts['main_menu_buttons'][user.language]
        await call.message.edit_text(message_to_user, reply_markup=await inline.main_menu_markup(buttons))

    await call.answer()
