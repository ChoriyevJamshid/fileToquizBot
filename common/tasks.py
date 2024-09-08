import re
import time

import requests
from celery import shared_task
from django.conf import settings

from tgbot.models import TelegramProfile
from common.models import Notification, FileTypeChoice
from tgbot.bot.utils import seconds_to_time


def clean_html_for_telegram(text):
    allowed_tags = {'b', 'i', 'u', 's', 'code', 'pre', 'br', 'a', 'em', 'strong', '\\n'}

    allowed_tags_re = '|'.join(allowed_tags)
    pattern = re.compile(r'</?(?!/?(?:{}))\w+[^>]*>'.format(allowed_tags_re), re.IGNORECASE)

    clean_text = re.sub(pattern, '', text)
    return clean_text.replace('<br>', '\n').replace('&nbsp;', ' ') \
        .replace('<br />', '').replace('&#39;', "'")


# @time_tester_decorator
def sync_send(user: TelegramProfile, notification: Notification):
    method = 'sendMessage'
    params = {
        'chat_id': user.chat_id,
        'parse_mode': 'HTML'
    }

    content = clean_html_for_telegram(notification.content)
    file = None
    if notification.file_id:
        file = notification.file_id

    if notification.file:
        file = settings.DOMAIN_URL + notification.file.url

    if notification.file_type == FileTypeChoice.VIDEO:
        method = 'sendVideo'
        params['video'] = file
        params['caption'] = content
    elif notification.file_type == FileTypeChoice.PHOTO:
        method = 'sendPhoto'
        params['photo'] = file
        params['caption'] = content
    elif notification.file_type == FileTypeChoice.AUDIO:
        method = 'sendAudio'
        params['audio'] = file
        params['caption'] = content
    else:
        params['text'] = content

    url = f'https://api.telegram.org/bot{settings.API_TOKEN}/{method}'
    try:
        response = requests.post(url, params=params)
    except Exception as e:
        return None

    return response


@shared_task
def send_notification(pk: int):

    notification = Notification.objects.filter(pk=pk).first()
    if not notification:
        return None

    if notification.ids != "all":
        ids = [int(_) for _ in notification.ids.split(',')]
        users = TelegramProfile.objects.filter(id__in=ids, is_notif=True)
    else:
        users = TelegramProfile.objects.filter(is_notif=True)
    users_count = len(users)
    cycles = users_count // 25 if not users_count % 25 else users_count // 25 + 1
    spent_time = 0

    for i in range(cycles):
        if (i + 1) * 25 < len(users):
            to = (i + 1) * 25
        else:
            to = len(users)

        start_time = time.perf_counter()
        for user in users[i * 25: to]:
            response = sync_send(user, notification)
        end_time = time.perf_counter()

        sp_time = round(end_time - start_time, 3)
        if end_time - start_time <= 1:
            time.sleep(1 - sp_time + 0.1)
        sp_time += spent_time

    notification.is_sent = True
    notification.is_sent_save(seconds_to_time(int(spent_time + 1)))
