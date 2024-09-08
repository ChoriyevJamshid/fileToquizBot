from datetime import datetime
from typing import Union, Optional, List

from django.db import models

from aiogram import Bot, types
from aiogram.enums import ChatMemberStatus
from aiogram.types import User, Chat

from common.models import RequiredChannel, Text, Language, Notification
from tgbot.models import TelegramProfile


def get_or_create_user(chat: Union[Chat, User]):
    user = TelegramProfile.objects.filter(chat_id=chat.id).first()

    if user is None:
        user = TelegramProfile(
            chat_id=chat.id,
            first_name=chat.first_name,
            last_name=chat.last_name,
            username=chat.username,
        )
        user.save()
    return user


async def get_user(chat: Union[Chat, User]):
    user = get_or_create_user(chat)
    return user


async def get_user_by_unique_field(**parameters):
    _q = models.Q()
    for field, value in parameters.items():
        _q.add(
            models.Q(**{"{}".format(field): value}), models.Q.OR
        )
    return TelegramProfile.objects.filter(_q).first()


async def get_users():
    return TelegramProfile.objects.all().values('id', 'chat_id', 'username', 'first_name').order_by('-created_at')


async def check_subscription(bot: Bot, user_id, channels):
    for channel in channels:
        member = await bot.get_chat_member(chat_id=channel.username,
                                           user_id=user_id)
        if member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED):
            return False
    return True


def get_channels():
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


async def save_user_notification(data: dict):

    chosen_users = list(data.get("chosen_users").values())
    if chosen_users[0] == "all":
        ids = "all"
    else:
        ids = ','.join([str(_) for _ in chosen_users])

    Notification.objects.create(
        content=data.get('content'),
        file_id=data.get('file_id'),
        file_type=data.get('file_type'),
        ids=ids,
        is_active=True,
    )


def resave_content(text: str, entities: Optional[List[types.MessageEntity]]):
    result = text
    data_entities = {
        'bold': ('<b>', '</b>'),
        'italic': ('<em>', '</em>'),
        'pre': ('<pre>', '</pre>'),
        'spoiler': ('<tg-spoiler>', '</tg-spoiler>'),
        'strikethrough': ('<strike>', '</strike>'),
        'phone_number': ('', ''),
        'url': ('', '')
    }
    if not entities:
        return text

    for entity in entities:
        offset = entity.offset
        length = entity.length
        _type = data_entities[entity.type]
        _sub_text = text[offset: offset + length + 1]
        result = result.replace(_sub_text, f"{_type[0]}{_sub_text}{_type[1]}")
    return result


def seconds_to_time(secs: int):
    hours = secs // 3600
    minutes = (secs % 3600) // 60
    seconds = secs % 60

    return datetime.strptime(f"{hours}:{minutes}:{seconds}", "%H:%M:%S").time()

