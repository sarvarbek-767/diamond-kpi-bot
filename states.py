from aiogram.fsm.state import State, StatesGroup

class EmployeeForm(StatesGroup):
    full_name = State()
    branch = State()
    position = State()
    telegram_id = State()

class KPIForm(StatesGroup):
    task_name = State()
    media = State()
    amount = State()

class EditKPIForm(StatesGroup):
    new_score = State()