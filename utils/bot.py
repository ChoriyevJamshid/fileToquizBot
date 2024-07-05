import requests
from django.conf import settings
from django.db.models import Q

URL = f'https://api.telegram.org/bot{settings.API_TOKEN}/'


def send_message(chat_id, text):
    url = URL + 'sendMessage'
    params = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        print(f"Message sent to chat_id {chat_id}")
    else:
        print(f"Failed to send message to chat_id {chat_id}: {response.text}")
    return response
