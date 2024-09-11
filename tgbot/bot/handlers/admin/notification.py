from typing import Dict
from aiogram import types
from aiogram.fsm.context import FSMContext

from tgbot.bot import utils
from tgbot.bot.keyboards import inline, reply
from tgbot.bot.states import CreateUserNotState


async def send_handler(message: types.Message, state: FSMContext, texts: Dict[str, Dict[str, str]]):
    await state.clear()
    user = await utils.get_user(message.chat)
    if not user.is_admin:
        return

    await message.answer(
        "✍️ Yubormoqchi bo'lgan xabarizni kiriting.",
        reply_markup=await reply.get_back_markup()
    )
    await state.set_state(CreateUserNotState.content)


async def get_content(message: types.Message, state: FSMContext, texts: Dict[str, Dict[str, str]]):
    if message.text.startswith('🔙'):
        await message.answer(
            f"🤖 <i>Admin panelga xush kelibsiz! 👇</i>"
            f"\n\n/notification - Reklama yuborish."
            f"\n/statistics - Statistika."
            f"\n/coupons - Kuponlar sonini yangilash."
            f"\n/instruction_photo_video - instruksiya."
        )
        return state.clear()

    content = utils.resave_content(message.text, message.entities)
    await state.update_data(content=content)
    await message.answer(
        f"📹 Media fayl yubormoqchi bo'lsangiz (<b>audio, video, photo</b>) "
        f"fayllardan birini yuklang, ask holda 👉  /skip",
        reply_markup=await reply.get_back_markup()
    )
    await state.set_state(CreateUserNotState.media)


async def get_media(message: types.Message, state: FSMContext, texts: Dict[str, Dict[str, str]]):
    if message.text and message.text.startswith("🔙"):
        await message.answer(
            "✍️ Yubormoqchi bo'lgan xabarizni kiriting.",
            reply_markup=await reply.get_back_markup()
        )
        return await state.set_state(CreateUserNotState.content)

    file_id, file_type = None, None

    if message.text != '/skip':
        if message.content_type == types.ContentType.PHOTO:

            file_id = message.photo[-1].file_id
            file_type = 'photo'

        elif message.content_type == types.ContentType.AUDIO:
            file_id = message.audio.file_id
            file_type = 'audio'

        elif message.content_type in (types.ContentType.VIDEO, types.ContentType.ANIMATION):
            file_id = message.video.file_id
            file_type = 'video'

        elif message.content_type == types.ContentType.DOCUMENT:
            extension = message.document.file_name.split('.')[-1]
            if extension in ('mp4', 'mpeg', 'avi', 'webm'):
                file_id = message.document.file_id
                file_type = 'video'
            else:
                return await message.answer("Iltimos to'g'ri ma'lumot kiriting!")

        else:
            return await message.answer("Iltimos to'g'ri ma'lumot kiriting!")

    await state.update_data({
        'file_id': file_id,
        'file_type': file_type,
    })

    data = await state.get_data()
    users = await utils.get_users()

    chosen_users = data.get('chosen_users', {})
    msg_to_user = ""
    total_users = len(users)
    paginate_by = 10
    page = 1

    total_page = total_users // paginate_by if not total_users % paginate_by else total_users // paginate_by + 1
    to = total_users if page * paginate_by > total_users else page * paginate_by

    users = users[(page - 1) * paginate_by: to]
    for index, user in enumerate(users, start=1):
        chat_id = user['chat_id']
        username = "@" + user['username'] if user['username'] else "-----"

        msg_to_user += (f"<b>{index}</b>. <i>Chat ID</i>: <code>{chat_id}</code>\n"
                        f"<i>Username</i>: <code>{username}</code>\n\n")

    await state.update_data(current_page=page, chosen_users=chosen_users)
    await message.answer(
        text="☑️ Xabardi kimlarga yubormoqchisiz ?\n"
             "<b>ID</b>, <b>Chat ID</b>, <b>Username</b> va <b>First Name</b> "
             "orqali qidirish mumkin.\n",
        reply_markup=await inline.admin_pagination_markup(state, users, total_page, page)
    )

    await state.set_state(CreateUserNotState.users)


async def back_to_media(message: types.Message, state: FSMContext, texts: Dict[str, Dict[str, str]]):
    try:
        await message.bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.message_id - 1,
            reply_markup=None
        )
    except Exception as e:
        pass

    await message.answer(
        f"📹 Media fayl yubormoqchi bo'lsangiz (<b>audio, video, photo</b>) "
        f"fayllardan birini yuklang, ask holda 👉  /skip",
        reply_markup=await reply.get_back_markup()
    )
    return await state.set_state(CreateUserNotState.media)


async def search_users(message: types.Message, state: FSMContext, texts: Dict[str, Dict[str, str]]):
    data = await state.get_data()
    chosen_users = data.get("chosen_users", {})
    page = data.get('current_page', 1)
    users = await utils.get_users()
    total_users = len(users)
    paginate_by = 10
    total_page = total_users // paginate_by if not total_users % paginate_by else total_users // paginate_by + 1
    to = total_users if page * paginate_by > total_users else page * paginate_by
    users = users[(page - 1) * paginate_by: to]

    if message.text.isdigit():
        _id = int(message.text)
        search_user = await utils.get_user_by_unique_field(**{"chat_id": _id, "id": _id})
    else:
        username = message.text[1:] if message.text.startswith("@") else message.text
        search_user = await utils.get_user_by_unique_field(**{"username": username})

    if not search_user:
        answer_text = f"‼️ <b>Bunday foydalanuvchi mavjud emas.</b>"
    else:
        if not chosen_users.get(str(search_user.chat_id)):
            answer_text = f"✅ <b>{message.text}</b> foydalanuvchi tanlandi."
            chosen_users[str(search_user.chat_id)] = search_user.id
            await state.update_data(chosen_users=chosen_users)
        else:
            answer_text = f"💬 Foydalanuvchi tanlab bo'lingan."
    try:
        await message.bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.message_id - 1,
            reply_markup=None
        )
    except Exception as e:
        pass

    await message.delete()
    await message.answer(
        answer_text,
        reply_markup=await inline.admin_pagination_markup(state, users, total_page, page)
    )


async def save_user_notification(message: types.Message, state: FSMContext, texts: Dict[str, Dict[str, str]]):
    data = await state.get_data()

    await message.answer(
        "✅ <b>Xabarnoma</b> saqlandi va foydalanuvchilarga yuborildi.",
        reply_markup=await reply.remove_markup()
    )
    await utils.save_user_notification(data)
    await state.clear()


async def choose_users(callback: types.CallbackQuery, state: FSMContext, texts: Dict[str, Dict[str, str]]):
    data = await state.get_data()
    current_page = int(data.get("current_page", 1))

    page = int(callback.data)

    if current_page == page:
        return await callback.answer()

    users = await utils.get_users()
    msg_to_user = ""
    total_users = len(users)
    paginate_by = 10

    total_page = total_users // paginate_by if not total_users % paginate_by else total_users // paginate_by + 1
    from_ = (page - 1) * paginate_by

    to = page * paginate_by

    if to > total_users:
        to = total_users

    _users = users[from_: to]

    for index, user in enumerate(_users, start=1 + from_):
        chat_id = user['chat_id']
        username = "@" + user['username'] if user['username'] else "-----"

        msg_to_user += (f"<b>{index}</b>. <i>Chat ID</i>: <code>{chat_id}</code>\n"
                        f"<i>Username</i>: <code>{username}</code>\n\n")

    await state.update_data(current_page=page)
    await callback.message.edit_reply_markup(
        reply_markup=await inline.admin_pagination_markup(state, _users, total_page, page)
    )
    await callback.answer()


async def check_chosen_users(callback: types.CallbackQuery, state: FSMContext, texts: Dict[str, Dict[str, str]]):
    data = await state.get_data()

    chosen_users = data.get('chosen_users', dict())
    page = int(data.get("current_page", 1))
    _, _id, chat_id = callback.data.split('_')

    users = await utils.get_users()
    total_users = len(users)
    paginate_by = 10

    total_page = total_users // paginate_by if not total_users % paginate_by else total_users // paginate_by + 1
    from_ = (page - 1) * paginate_by

    to = page * paginate_by

    if to > total_users:
        to = total_users

    users = users[from_: to]

    if not chosen_users.get(str(chat_id), None):
        chosen_users[str(chat_id)] = int(_id)
    else:
        del chosen_users[str(chat_id)]

    await state.update_data(chosen_users=chosen_users)
    await callback.message.edit_reply_markup(
        reply_markup=await inline.admin_pagination_markup(state, users, total_page, page)
    )


async def save_users(callback: types.CallbackQuery, state: FSMContext, texts: Dict[str, Dict[str, str]]):
    data = await state.get_data()
    content = data.get("content")
    file_id = data.get('file_id')
    file_type = data.get('file_type')

    if callback.data.split('_')[-1] == 'all':
        await state.update_data(chosen_users={'all': 'all'})

    text = (f"<b>Xabarnoma</b>\n"
            f"<b>Matni</b>: {content}\n")
    markup = await reply.save_markup()
    await callback.message.delete_reply_markup()
    if file_type and file_id:
        if file_type == 'photo':
            text += "<b>Media</b>: photo"
            await callback.message.answer_photo(file_id, f"\n{text}", reply_markup=markup)
        elif file_type == 'audio':
            text += "<b>Media</b>: audio"
            await callback.message.answer_audio(file_id, f"\n{text}", reply_markup=markup)
        else:
            text += "<b>Media</b>: video"
            await callback.message.answer_video(file_id, caption=f"\n{text}", reply_markup=markup)
    else:
        text += "<b>Media</b>: mavjud emas"
        await callback.message.answer(f"\n{text}", reply_markup=markup)
    content = (f"<b>Admindan xabarnoma</b>: "
               f"{content}")
    await state.update_data(content=content)
    await state.set_state(CreateUserNotState.save)
