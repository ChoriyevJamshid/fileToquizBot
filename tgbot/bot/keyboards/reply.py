from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton


async def generate_markup(items: list | tuple, sizes: tuple):
    markup = ReplyKeyboardBuilder()
    for item in items:
        markup.add(
            KeyboardButton(text=str(item))
        )
    return markup.adjust(*sizes).as_markup(resize_keyboard=True)


async def duration_markup():
    items = [i for i in range(10, 61, 5)]
    markup = await generate_markup(items, (2,))
    return markup


async def quantity_markup():
    items = (20, 25, 30, 35, 40, 45, 50)
    markup = await generate_markup(items, (2,))
    return markup


async def instruction_markup(buttons):
    items = (f"📝 {buttons[1]}", f"🎬 {buttons[2]}", f"🔙 {buttons[3]}")
    return await generate_markup(items, (2,))
