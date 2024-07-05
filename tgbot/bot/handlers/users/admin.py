from aiogram import Bot, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from tgbot.bot.handlers.users import dp_user
from tgbot.bot.utils import get_user

from tgbot.models import Data


@dp_user.message(F.photo)
async def get_photo(message: types.Message, state: FSMContext, bot: Bot):
    user = await get_user(state, message.chat.id)
    if user.is_admin and message.caption == "/photo":
        _data = Data.get_solo()
        data = _data.data
        file_id = message.photo[-1].file_id
        instruction = data.get('instruction', None)
        if instruction is None:
            instruction = data['instruction'] = dict()

        instruction['photo'] = file_id
        data['instruction'] = instruction
        _data.save()

        await message.answer(
            "Photo has been saved"
        )


