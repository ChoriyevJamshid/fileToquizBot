from aiogram import Bot, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from tgbot.bot.handlers.users import dp_user
from tgbot.bot.utils import get_user

from tgbot.models import Data


@dp_user.message(Command("admin"))
async def admin(message: types.Message, state: FSMContext):
    user = await get_user(state, message.chat.id)

    if user.is_admin:
        await message.answer(
            text="Help texts with photo: word, excel, txt, csv\nHelp texts with video: word, excel, txt, csv"
        )


@dp_user.message(F.animation)
@dp_user.message(F.video)
@dp_user.message(F.photo)
async def get_photo(message: types.Message, state: FSMContext, bot: Bot):
    user = await get_user(state, message.chat.id)

    if user.is_admin:
        data = Data.get_solo()
        if message.content_type == types.ContentType.PHOTO:
            content = data.data['instruction']['photo']
            content_type = "photo"
            file_id = message.photo[-1].file_id
        else:
            content = data.data['instruction']['video']
            content_type = "video"
            try:
                file_id = message.video.file_id
            except AttributeError:
                file_id = message.animation.file_id
        if message.caption in ("word", "excel", "txt", "csv"):
            content[message.caption] = file_id
            data.data['instruction'][content_type] = content
            data.save()
            await message.answer(
                f"{content_type.title()} has been saved"
            )
        else:
            await message.answer(
                f"{content_type.title()} not saved! Extension not valid!"
            )
    else:
        await message.delete()
