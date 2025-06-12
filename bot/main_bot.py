import asyncio
import os
import logging
from dotenv import load_dotenv

from aiogram import Router, F, Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from bot.inline_yes_button import show_full_result_kb
from bot.states import SalaryInput
from salary_dgs.models import BaseSalary, GetDataSalary
from salary_dgs.services import CalculationBaseSalary

router = Router()

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
                logging.FileHandler("bot.log", encoding="utf-8"),  # Логи в файл
                logging.StreamHandler(),  # Логи в консоль (можно убрать)
        ],
)

logger = logging.getLogger(__name__)


# 🟢 Стартовая команда
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_data({"salary": BaseSalary()})
    await state.set_state(SalaryInput.base_salary)
    await message.answer(
            "Привет! Я посчитаю Вашу зарплату!\n"
            "Укажите ваш оклад: "
    )
    logger.info(f"Команда /start, пользователь {message.from_user.username}")
    logger.info(
            f"Введен оклад {message.text} пользователю {message.from_user.username}"
    )


# Получение месяца
@router.message(StateFilter(SalaryInput.base_salary), F.text)
async def input_base_salary(message: Message, state: FSMContext):
    data = await state.get_data()
    salary: BaseSalary = data["salary"]
    try:
        salary.base_salary = message.text
        await state.update_data(salary=salary)
        await state.set_state(SalaryInput.month)
        await message.answer("Введите расчетный месяц: ")
        logger.info(
                f"Введен месяц {message.text} пользователю {message.from_user.username}"
        )
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
                f"Ошибка ввода месяца {message.text} пользователю {message.from_user.username}"
        )


# Получение рабочих дней
@router.message(StateFilter(SalaryInput.month), F.text)
async def input_month(message: Message, state: FSMContext):
    data = await state.get_data()
    salary: BaseSalary = data["salary"]
    try:
        salary.month = message.text
        await state.update_data(salary=salary)
        await state.set_state(SalaryInput.sum_days)
        await message.answer("Введите общее количество отработанных или планируемых смен: ")
        logger.info(
                f"Введено количество рабочих дней {message.text} пользователем {message.from_user.username}"
        )
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
                f"Ошибка ввода месяца {message.text} пользователем {message.from_user.username}"
        )


# Получение ночных смен
@router.message(StateFilter(SalaryInput.sum_days), F.text)
async def input_sum_days(message: Message, state: FSMContext):
    data = await state.get_data()
    salary: BaseSalary = data["salary"]
    try:
        salary.sum_days = message.text
        await state.update_data(salary=salary)
        await state.set_state(SalaryInput.night_shifts)
        await message.answer(
                "Введите количество ночных смен\n" "Введите 0, если таковых нет: "
        )
        logger.info(
                f"Введено количество ночных смен {message.text} пользователем {message.from_user.username}"
        )
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
                f"Ошибка ввода ночных смен {message.text} пользователем {message.from_user.username}"
        )


# Получение вечерних смен
@router.message(StateFilter(SalaryInput.night_shifts), F.text)
async def input_night_shifts(message: Message, state: FSMContext):
    data = await state.get_data()
    salary: BaseSalary = data["salary"]
    try:
        salary.night_shifts = message.text
        await state.update_data(salary=salary)
        await state.set_state(SalaryInput.evening_shifts)
        await message.answer(
                "Введите количество вечерних смен\n" "Введите 0, если таковых нет: "
        )
        logger.info(
                f"Введено количество вечерних смен {message.text} пользователем {message.from_user.username}"
        )
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
                f"Ошибка ввода вечерних смен {message.text} пользователем {message.from_user.username}"
        )


# Получение времени отработанных при температуре
@router.message(StateFilter(SalaryInput.evening_shifts), F.text)
async def input_evening_shifts(message: Message, state: FSMContext):
    data = await state.get_data()
    salary: BaseSalary = data["salary"]
    try:
        salary.evening_shifts = message.text
        await state.update_data(salary=salary)
        await state.set_state(SalaryInput.temperature_work)
        await message.answer(
                "Введите количество смен работы в температуре свыше +26 градусов\n"
                "Введите 0, если таковых нет: "
        )
        logger.info(
                f"Введено количество смен работы в температуре {message.text} "
                f"пользователем {message.from_user.username}"
        )
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
                f"Ошибка ввода количество смен работы в температуре {message.text} "
                f"пользователем {message.from_user.username} - {e}"
        )


# Получение информации по налоговому вычету
@router.message(StateFilter(SalaryInput.temperature_work), F.text)
async def input_temperature_work(message: Message, state: FSMContext):
    data = await state.get_data()
    salary: BaseSalary = data["salary"]
    try:
        salary.temperature_work = message.text
        await state.update_data(salary=salary)
        await state.set_state(SalaryInput.children)
        await message.answer(
                "Введите через запятую данные детей на которых производится налоговый вычет в формате:\n"
                "Нет налогового вычета укажите: 0\n"
                "на 1-го и 2-го: 1,2\n"
                "на 2-го и 3-го: 2,3, и т.д.\n\n"
                "Для справки:\n"
                "на первого ребенка налоговый вычет составляет - 1400 ₽\n"
                "на второго ребенка налоговый вычет составляет - 1600 ₽\n"
                "на третьего ребенка и последующих налоговый вычет составляет - 6000 ₽\n"
                "Если первый ребенок уже повзрослел и на него вычет уже не производится "
                "то на последующих детей сумма вычета не меняется.\n"
                "Данные вычеты суммируются, сумма облагается налогом в размере 13% "
                "и итоговая сумма остается в ваших начислениях."
        )
        logger.info(
                f"Введено количество детей на налоговый вычет {message.text} "
                f"пользователем {message.from_user.username}"
        )
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
                f"Ошибка ввода количество детей дошкольного возраста {message.text} "
                f"пользователем {message.from_user.username} - {e}"
        )


# Получение информации по алиментам
@router.message(StateFilter(SalaryInput.children), F.text)
async def input_children(message: Message, state: FSMContext):
    data = await state.get_data()
    salary: BaseSalary = data["salary"]
    try:
        salary.children = message.text
        await state.update_data(salary=salary)
        await state.set_state(SalaryInput.alimony)
        await message.answer(
                "Введите через запятую или одним числом процент по алиментам.\n"
                "Нет алиментов укажите: 0\n\n"
                "Примеры ввода:\n"
                "От одного брака один ребенок: 25\n"
                "От одного брака два ребенка: 33\n"
                "От одного брака три ребенка и более: 50\n"
                "От разных браков: 25,25 или 25,16 или 33,25 или 50,25"
        )
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
                f"Ошибка ввода алиментов {message.text} "
                f"пользователем {message.from_user.username} - {e}"
        )


# Итоговый вывод
@router.message(StateFilter(SalaryInput.alimony), F.text)
async def input_alimony(message: Message, state: FSMContext):
    data = await state.get_data()
    salary: BaseSalary = data["salary"]

    try:
        salary.alimony = message.text
        await state.update_data(salary=salary)

        # Преобразуем в GetDataSalary
        get_salary = GetDataSalary(
                _base_salary=salary.base_salary,
                _month=salary.month,
                _sum_days=salary.sum_days,
                _night_shifts=salary.night_shifts,
                _evening_shifts=salary.evening_shifts,
                _temperature_work=salary.temperature_work,
                _children=salary.children,
                _alimony=salary.alimony,
        )

        # Начислено
        calc = CalculationBaseSalary(get_salary)

        result_answer = await calc.calculation_answer()
        result_base_month = await calc.calculation_base_month()
        result_month_quarter = await calc.month_quarter_payment_calculation()

        await message.answer(f"✅ Итоговая сумма к выплате: {result_answer} ₽\n"
                            f"👆 Дополнительно Вам будет выплачено: {result_base_month} ₽\n"
                            f"в {result_month_quarter}.")
        await message.answer(
                f"Вам предоставить полные данные по расчету?\n",
                reply_markup=show_full_result_kb
        )

        # Переводим в состояние ожидания ответа
        await state.set_state(SalaryInput.show_full_result)

    except ValueError as e:
        await message.answer(f"Ошибка: {e}")


@router.callback_query(StateFilter(SalaryInput.show_full_result), F.data == "show_full_result")
async def show_full_result_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    salary: BaseSalary = data["salary"]

    get_salary = GetDataSalary(
        _base_salary=salary.base_salary,
        _month=salary.month,
        _sum_days=salary.sum_days,
        _night_shifts=salary.night_shifts,
        _evening_shifts=salary.evening_shifts,
        _temperature_work=salary.temperature_work,
        _children=salary.children,
        _alimony=salary.alimony,
    )

    calc = CalculationBaseSalary(get_salary)

    result_base_salary = await calc.calculation_base_salary()
    result_night_shifts = await calc.calculation_night_shifts()
    result_bonus = await calc.calculation_bonus()
    result_underground = await calc.calculation_underground()
    result_in_temperature = await calc.calculation_working_in_temperature()
    result_district_allowance = await calc.calculation_district_allowance()
    result_north_allowance = await calc.calculation_north_allowance()
    result_total_accruals = await calc.calculation_total_accruals()
    result_deduction_for_children = await calc.calculation_deduction_for_children()
    result_withholding_tax = await calc.calculation_withholding_tax()
    result_alimony = await calc.calculation_alimony()
    result_answer = await calc.calculation_answer()
    result_base_month = await calc.calculation_base_month()
    result_month_quarter = await calc.month_quarter_payment_calculation()

    await callback.message.answer(
        f"НАЧИСЛЕНО:\n"
        f"Оклад за фактическое отработанное время: {result_base_salary} ₽\n"
        f"Доплата за работу в ночное время: {result_night_shifts} ₽\n"
        f"Премия ежемесячная: {result_bonus} ₽\n"
        f"Надбавка за вредные условия труда: {result_underground} ₽\n"
        f"Доплата за работу в температуре свыше +26С: {result_in_temperature} ₽\n"
        f"Районный коэффициент: {result_district_allowance} ₽\n"
        f"Северная надбавка: {result_north_allowance} ₽\n"
        f"Налоговый вычет на детей: {result_deduction_for_children} ₽\n\n"
        f"✅ ИТОГО НАЧИСЛЕНИЯ: {result_total_accruals} ₽\n"
    )
    await callback.message.answer(
        f"УДЕРЖАНО:\n"
        f"Налог с начислений (НДФЛ): {result_withholding_tax} ₽\n"
        f"Алименты: {result_alimony} ₽\n"
        f"✅ ИТОГО К ВЫПЛАТЕ: {result_answer} ₽\n"
        f"👆 Дополнительно Вам будет выплачено: {result_base_month} ₽\n"
        f"в {result_month_quarter}."
    )

    await callback.answer()
    await state.clear()


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
