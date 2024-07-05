from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.types import User

from common.models import RequiredChannel, Text, Language
from tgbot.models import TelegramProfile


def get_or_create_user(chat_id, first_name=None, last_name=None, username=None):
    user = TelegramProfile.objects.filter(chat_id=chat_id).first()

    if user is None:
        user = TelegramProfile(
            chat_id=chat_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
        )
        user.save()
    return user


async def get_user(state, chat_id, first_name=None, last_name=None, username=None):
    data = await state.get_data()
    user = data.get(str(chat_id))
    if user is None:
        user = get_or_create_user(chat_id, first_name, last_name, username)
    return user


async def check_subscription(bot: Bot, user_id, channels):
    for channel in channels:
        member = await bot.get_chat_member(chat_id=channel.username,
                                           user_id=user_id)
        if member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED):
            return False
    return True


def get_channels(session=None):
    return RequiredChannel.objects.all()


async def get_texts(state):
    data = await state.get_data()
    texts = data.get("texts")
    if texts is None:
        texts = Text.texts_data()
        await state.update_data(texts=texts)
    return texts


async def get_languages(state):
    data = await state.get_data()
    languages = data.get("languages")
    if languages is None:
        languages = Language.objects.all()
        await state.update_data(languages=languages)
    return languages
