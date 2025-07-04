from bot.keyboards import show_months_of_years, back_button_kb
from bot.states import SalaryInput

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message


async def prompt_for_state(message: Message, state: FSMContext, target_state: State):
    await state.set_state(target_state)

    if target_state == SalaryInput.base_salary:
        await message.answer("Укажите ваш оклад:")
    elif target_state == SalaryInput.month:
        await message.answer("Введите расчетный месяц:", reply_markup=show_months_of_years)
    elif target_state == SalaryInput.sum_days:
        await message.answer(
                "Введите общее количество отработанных или планируемых смен:",
                reply_markup=back_button_kb,
        )
    elif target_state == SalaryInput.night_shifts:
        await message.answer(
                "Введите количество ночных смен:", reply_markup=back_button_kb
        )
    elif target_state == SalaryInput.evening_shifts:
        await message.answer(
                "Введите количество вечерних смен:", reply_markup=back_button_kb
        )
    elif target_state == SalaryInput.temperature_work:
        await message.answer(
                "Введите количество смен работы в температуре свыше +26 градусов:",
                reply_markup=back_button_kb,
        )
    elif target_state == SalaryInput.children:
        await message.answer(
                "Введите через запятую данные детей на которых производится налоговый вычет:",
                reply_markup=back_button_kb,
        )
    elif target_state == SalaryInput.alimony:
        await message.answer(
                "Введите через запятую или одним числом процент по алиментам:",
                reply_markup=back_button_kb,
        )