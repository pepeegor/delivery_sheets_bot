from aiogram.fsm.state import State, StatesGroup

class OrderStates(StatesGroup):
    track_codes = State()
    name = State()
    phone = State()
    address = State()