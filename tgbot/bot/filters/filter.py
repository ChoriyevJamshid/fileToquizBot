from aiogram.filters import Filter
from aiogram import types

from common.models import Text
from tgbot.bot.handlers.group_functions import save_user_answer
from tgbot.models import UserQuizPart, Data



class ChatTypeFilter(Filter):
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types


class UserActiveQuizFilter(Filter):
    def __init__(self) -> None:
        self.texts = Text.texts_data()

    async def __call__(self, obj: types.Message | types.CallbackQuery) -> bool:
        if isinstance(obj, types.Message):
            if obj.text != "/stop":
                quiz = UserQuizPart.objects.filter(user__chat_id=obj.chat.id, is_active=True).select_related(
                    "user"
                ).first()
                if quiz:
                    await obj.delete()
                    await obj.bot.send_message(
                        chat_id=obj.chat.id,
                        text=self.texts['filter_text'][quiz.user.language]
                    )
                    return False

        elif isinstance(obj, types.CallbackQuery):
            quiz = UserQuizPart.objects.filter(user__chat_id=obj.message.chat.id, is_active=True).select_related(
                "user"
            ).first()
            if quiz:
                await obj.bot.send_message(
                    chat_id=obj.chat.id,
                    text=self.texts['filter_text'][quiz.user.language]
                )
                return False
        return True


class PollAnswerFilter(Filter):
    def __init__(self):
        pass

    async def __call__(self, poll_answer: types.PollAnswer) -> bool:
        groups = Data.get_solo().data['groups']
        poll_id = poll_answer.poll_id
        if not groups.get(poll_id, None):
            return True
        await save_user_answer(groups[str(poll_id)], poll_answer)
        return False
