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

