from aiogram.fsm.state import StatesGroup, State


class NewQuizState(StatesGroup):
    title = State()
    file = State()
    quantity = State()
    duration = State()
    max_option = State()


class InstructionState(StatesGroup):
    instruction = State()
    text = State()
    video = State()


class CreateUserNotState(StatesGroup):
    content = State()
    media = State()
    users = State()
    save = State()

class AdminState(StatesGroup):
    coupons = State()

