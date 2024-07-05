import asyncio
from django.conf import settings
from django.core.management import BaseCommand
from utils.bot import send_message
from tgbot.bot.app import main


class Command(BaseCommand):
    help = 'Run the bot'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting bot...'))
        for admin in settings.ADMINS:
            send_message(chat_id=admin, text='Bot has been started!')
        asyncio.run(main())

