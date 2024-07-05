from aiogram import Bot, types, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import User

from tgbot.bot.filters.filter import ChatTypeFilter
from tgbot.bot.utils import get_user
from tgbot.models import QuizPart

dp_group = Router()
dp_group.message.filter(ChatTypeFilter(['group', 'supergroup']))


@dp_group.message(CommandStart())
async def start(message: types.Message, state: FSMContext, bot: Bot):
    print(message.text)
    message_data = message.text.split(" ")
    user_id = message.from_user.id
    user = await get_user(state, user_id)

    if len(message_data) == 2:
        link = message_data[-1]
        quiz_part = QuizPart.objects.filter(link=link)
        if quiz_part.exists():
            quiz = quiz_part.first()
