from aiogram import types, F

from tgbot.bot.handlers.users import dp_user
from tgbot.bot.keyboards import inline
from tgbot.bot.utils import get_user

from tgbot.models import Data


@dp_user.callback_query(F.data.startswith("instruction"))
async def instruction_callback(call: types.CallbackQuery, texts: dict):
    user = await get_user(call.from_user)

    language = user.language if user.language else 'uz'

    buttons = texts['instruction_buttons'][language]
    back_btn = texts['back'][language]
    call_data = call.data.split("_")[-1]

    if not user.is_verified:
        user.is_verified = True
        user.save(update_fields=['is_verified'])

    if call_data == buttons[1]:

        markup = await inline.generate_markup(
            buttons={
                "Word": 'file_photo_word',
                "Excel": "file_photo_excel",
                "PDF": "file_photo_pdf",
                "Text": "file_photo_txt",
                "Csv": "file_photo_csv",
                f"🔙 {back_btn}": "file_photo_back"
            },
            sizes=(1,)
        )
        await call.message.edit_reply_markup(reply_markup=markup)

    elif call_data == buttons[2]:
        markup = await inline.generate_markup(
            buttons={
                "Word": 'file_video_word',
                "Excel": "file_video_excel",
                "PDF": "file_video_pdf",
                "Text": "file_video_txt",
                "Csv": "file_video_csv",
                f"🔙 {back_btn}": "file_video_back"
            },
            sizes=(1,)
        )
        await call.message.edit_reply_markup(reply_markup=markup)

    else:
        message_to_user = f"🤖 {texts['menu'][language]} ⬇️"
        buttons = texts['main_menu_buttons'][language]
        await call.message.edit_text(message_to_user, reply_markup=await inline.main_menu_markup(
            buttons, texts, language))

    await call.answer()


@dp_user.callback_query(F.data.startswith("file"))
async def instruction_files_callback(call: types.CallbackQuery, texts: dict):

    user = await get_user(call.from_user)
    data = Data.get_solo()

    _, content_type, file_type = call.data.split("_")
    if file_type in ("word", "excel", "txt", "csv", "pdf"):
        file_id = data.data['instruction'][content_type][file_type]
    else:
        buttons = texts['instruction_buttons'][user.language]
        message_to_user = (f"🗞 <b>{texts['instruction'][user.language]}.</b>\n"
                           f"{texts['instruction_text'][user.language]}")
        return await call.message.edit_text(
            message_to_user, reply_markup=await inline.instruction_markup(buttons, (2,))
        )

    if file_id:
        if content_type == "photo":
            await call.message.answer_photo(photo=file_id)
        else:
            await call.message.answer_video(video=file_id)
    else:
        msg_to_user = f"🎬 {texts['no_video_instruction'][user.language]} 😔\n\n👉 /start"
        if content_type == "photo":
            msg_to_user = f"📝 {texts['no_text_instruction'][user.language]} 😔\n\n👉 /start"
        await call.message.answer(msg_to_user)
    await call.answer()


