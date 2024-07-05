import asyncio

from config.settings import API_TOKEN
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from django.conf import settings

from tgbot.bot.handlers import dp_user, dp_group

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()
dp.include_router(dp_user)
dp.include_router(dp_group)


async def on_startup():
    pass


async def on_shutdown():
    pass


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await bot.delete_webhook(drop_pending_updates=True)
    # await bot.set_my_commands()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
