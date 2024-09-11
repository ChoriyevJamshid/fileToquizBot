from aiogram import Router, F
from aiogram.filters import Command

from tgbot.bot.handlers.admin.common import *
from tgbot.bot.handlers.admin.notification import *


def prepare_router() -> Router:

    router = Router()
    router.message.register(admin_handler, Command('admin'))
    router.message.register(statistics, Command('statistics'))
    router.message.register(test_send_document, Command('doc'))

    router.message.register(change_coupons, Command('coupons'))
    router.message.register(get_coupons, AdminState.coupons)

    router.message.register(send_handler, Command('notification'))
    router.message.register(get_content, CreateUserNotState.content)
    router.message.register(get_media, CreateUserNotState.media)
    router.message.register(back_to_media, F.text.startswith("🔙"), CreateUserNotState.users)
    router.message.register(search_users, CreateUserNotState.users)
    router.message.register(save_user_notification, CreateUserNotState.save)
    router.callback_query.register(check_chosen_users, F.data.startswith("choose-user"))
    router.callback_query.register(save_users, F.data.startswith("save-users"))
    router.callback_query.register(choose_users, CreateUserNotState.users)

    return router
