from typing import Optional
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton
from aiogram.types import ReplyKeyboardRemove


async def generate_markup(items: list | tuple, sizes: tuple, texts: Optional[dict], language: Optional[str]):
    markup = ReplyKeyboardBuilder()
    for item in items:
        markup.add(
            KeyboardButton(text=str(item))
        )
    back_text = "🔙"
    if texts:
        back_text = "🔙 " + texts['back'][language]

    markup.adjust(*sizes)
    markup.attach(
        ReplyKeyboardBuilder().add(
            KeyboardButton(text=back_text)
        ).adjust(*(1,))
    )
    return markup.as_markup(resize_keyboard=True)


async def duration_markup(texts: dict, language: str):
    text = texts['seconds'][language]
    items = [f"{i} {text}" for i in range(10, 61, 5)]
    markup = await generate_markup(items, (2,), texts, language)

    return markup


async def quantity_markup(texts: Optional[dict], language: Optional[str]):
    items = (20, 25, 30, 35, 40, 45, 50)
    markup = await generate_markup(items, (2,), texts, language)
    return markup


async def instruction_markup(buttons, texts: Optional[dict], language: Optional[str]):
    items = (f"📝 {buttons[1]}", f"🎬 {buttons[2]}", f"🔙 {buttons[3]}")
    return await generate_markup(items, (2,), texts, language)


async def remove_markup():
    return ReplyKeyboardRemove()
