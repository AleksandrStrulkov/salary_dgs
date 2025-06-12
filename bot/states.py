from aiogram.fsm.state import State, StatesGroup


class SalaryInput(StatesGroup):
    base_salary = State()
    month = State()
    sum_days = State()
    night_shifts = State()
    evening_shifts = State()
    temperature_work = State()
    children = State()
    alimony = State()
