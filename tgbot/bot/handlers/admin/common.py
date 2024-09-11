from typing import Dict

from aiogram import types
from aiogram.fsm.context import FSMContext

from tgbot.bot import utils, queries
from tgbot.bot.states import AdminState


async def admin_handler(message: types.Message, state: FSMContext, texts: Dict[str, Dict[str, str]]):
    user = await utils.get_user(message.chat)

    if not user.is_admin:
        return

    await message.answer(
        f"🤖 <i>Admin panelga xush kelibsiz! 👇</i>"
        f"\n\n/notification - Reklama yuborish."
        f"\n/statistics - Statistika."
        f"\n/coupons - Kuponlar sonini yangilash."
        f"\n/instruction_photo_video - instruksiya."
    )


async def statistics(message: types.Message, state: FSMContext, texts: Dict[str, Dict[str, str]]):
    user = await utils.get_user(message.chat)

    if not user.is_admin:
        return await message.delete()

    users_statistics = await queries.get_users_statistics()

    msg_text_user = (f"👤 <b>Foydalanuvchilar soni</b>\n"
                     f"Oxirgi kundagi: <b>{users_statistics['day_count']}</b> ta.\n"
                     f"Oxirgi haftadagi: <b>{users_statistics['week_count']}</b> ta.\n"
                     f"Oxirgi oydagi: <b>{users_statistics['month_count']}</b> ta.\n"
                     f"Umumiy: <b>{users_statistics['count']}</b> ta.\n\n")

    await message.answer(msg_text_user)


async def test_send_document(message: types.Message, state: FSMContext):

    await message.answer_video(video="BQACAgIAAxkBAAIWeGbdXITs9Xp4Oe_swn8lmUjN0GmPAAKCVAACOKXpSgS2Fgn6gSuwNgQ")
    # await message.answer_document()


async def change_coupons(message: types.Message, state: FSMContext):
    user = await utils.get_user(message.chat)

    if not user.is_admin: return

    await message.answer(
        "💬 Kuponlar sonini kiriting."
    )
    await state.set_state(AdminState.coupons)


async def get_coupons(message: types.Message, state: FSMContext):

    if message.text.isdigit():
        number = int(message.text)
        await utils.update_users_coupon(number)
        await message.answer("✅ Kuponlar soni yangilandi.")
        await state.clear()
    else:
        await message.answer("✅ Son kiriting!")

