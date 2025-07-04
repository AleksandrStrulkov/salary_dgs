import logging
from aiogram import Router, F, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State


from bot.keyboards import show_full_result_kb, main_menu_kb, main_menu_start, get_back_finish_kb, combined_keyboard
from bot.promt_for_state import prompt_for_state
from bot.states import SalaryInput
from salary_dgs.constant import EN_TO_RU_MONTHS
from \
    salary_dgs.models import BaseSalary, GetDataSalary
from salary_dgs.services import CalculationBaseSalary

router = Router()

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
                logging.FileHandler("bot.log", encoding="utf-8"),  # Логи в файл
                logging.StreamHandler(),  # Логи в консоль (можно убрать)
        ],
)

logger = logging.getLogger(__name__)

step_sequence = [
        SalaryInput.base_salary,
        SalaryInput.month,
        SalaryInput.sum_days,
        SalaryInput.night_shifts,
        SalaryInput.evening_shifts,
        SalaryInput.temperature_work,
        SalaryInput.children,
        SalaryInput.alimony,
        SalaryInput.show_full_result,
]


def restore_salary(data: dict) -> BaseSalary:
    salary_data = data.get("salary")
    if isinstance(salary_data, BaseSalary):
        return salary_data
    return BaseSalary.from_dict(salary_data)


def get_previous_state(current_state: State) -> State | None:
    try:
        index = step_sequence.index(current_state)
        if index > 0:
            return step_sequence[index - 1]
    except ValueError:
        pass
    return None


# 🟢 Стартовая команда
@router.callback_query(F.data == "start")
async def start_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_data({"salary": BaseSalary()})
    await state.set_state(SalaryInput.base_salary)
    await callback.message.answer("💰 Укажите Ваш оклад:")

    logger.info(f"Команда /start, пользователь")
    user = callback.from_user
    full_name = user.full_name
    logger.info(f"Введен оклад пользователем - {full_name}")
    await callback.answer()


@router.callback_query(F.data == "stop")
async def stop_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("✅ Ввод данных остановлен. Вы можете начать заново.", reply_markup=main_menu_start)
    await callback.answer()


@router.callback_query(StateFilter(SalaryInput.show_full_result), F.data == "finish")
async def finish_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("✅ Расчёт завершён. Спасибо за использование бота!")
    await callback.answer()
    await state.clear()


# Получение месяца
@router.message(StateFilter(SalaryInput.base_salary), F.text)
async def input_base_salary(message: Message, state: FSMContext):
    data = await state.get_data()
    salary = restore_salary(await state.get_data())
    user = message.from_user
    full_name = user.full_name
    try:
        salary.base_salary = message.text
        await state.update_data(salary=salary.to_dict())
        await state.set_state(SalaryInput.month)
        await message.answer("📅 Выберите расчетный месяц:", reply_markup=combined_keyboard)

        logger.info(f"Введен месяц {message.text} ({full_name})")
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
                f"Ошибка ввода месяца {message.text} - {e} - ({full_name})"
        )


@router.callback_query(StateFilter(SalaryInput.month), F.data.startswith("month_"))
async def select_month(callback: CallbackQuery, state: FSMContext):
    en_month = callback.data.replace("month_", "").lower()
    ru_month = EN_TO_RU_MONTHS.get(en_month)
    user = callback.from_user
    full_name = user.full_name

    if ru_month is None:
        await callback.answer("Ошибка: неизвестный месяц")
        return

    data = await state.get_data()
    salary_data = data.get("salary")

    if isinstance(salary_data, BaseSalary):
        salary = salary_data
    else:
        salary = BaseSalary.from_dict(salary_data)

    salary.month = ru_month
    await state.update_data(salary=salary.to_dict())

    await callback.answer(f"Выбран месяц: {ru_month.capitalize()}")

    # Переход к следующему шагу
    await state.set_state(SalaryInput.sum_days)

    # Запрос ввода количества смен
    try:
        await callback.message.answer(
                "⏱️ Введите общее количество смен:",
                reply_markup=get_back_finish_kb(),
        )
        logger.info(f"Введено всего смен {callback.message.text} ({full_name})")
    except ValueError as e:
        await callback.message.answer(f"Ошибка: {e}")
        logger.error(
                f"Ошибка ввода ночных смен {callback.message.text} - {e} - ({full_name})"
        )


# Получение ночных смен
@router.message(StateFilter(SalaryInput.sum_days), F.text)
async def input_sum_days(message: Message, state: FSMContext):
    data = await state.get_data()
    salary = restore_salary(await state.get_data())
    user = message.from_user
    full_name = user.full_name
    try:
        salary.sum_days = message.text
        await state.update_data(salary=salary)
        await state.set_state(SalaryInput.night_shifts)
        await message.answer(
                "🌙 Введите количество ночных смен.\n" "Введите 0, если таковых нет:",
                reply_markup=get_back_finish_kb(),
        )
        logger.info(
                f"Введено количество ночных смен {message.text} ({full_name})"
        )
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
                f"Ошибка ввода ночных смен {message.text} - {e} - ({full_name})"
        )


# Получение вечерних смен
@router.message(StateFilter(SalaryInput.night_shifts), F.text)
async def input_night_shifts(message: Message, state: FSMContext):
    data = await state.get_data()
    salary = restore_salary(await state.get_data())
    user = message.from_user
    full_name = user.full_name
    try:
        salary.night_shifts = message.text
        await state.update_data(salary=salary)
        await state.set_state(SalaryInput.evening_shifts)
        await message.answer(
                "🕕 Введите количество вечерних смен.\n" "Введите 0, если таковых нет:",
                reply_markup=get_back_finish_kb(),
        )
        logger.info(
                f"Введено количество вечерних смен {message.text} ({full_name})"
        )
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
                f"Ошибка ввода вечерних смен {message.text} - {e} - ({full_name})"
        )


# Получение времени отработанных при температуре
@router.message(StateFilter(SalaryInput.evening_shifts), F.text)
async def input_evening_shifts(message: Message, state: FSMContext):
    data = await state.get_data()
    salary = restore_salary(await state.get_data())
    user = message.from_user
    full_name = user.full_name
    try:
        salary.evening_shifts = message.text
        await state.update_data(salary=salary)
        await state.set_state(SalaryInput.temperature_work)
        await message.answer(
                "🌡️ Введите количество смен работы в температуре свыше +26 градусов.\n"
                "Введите 0, если таковых нет:",
                reply_markup=get_back_finish_kb(),
        )
        logger.info(
                f"Введено количество смен работы в температуре {message.text} ({full_name})"
        )
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
                f"Ошибка ввода количества смен работы в температуре {message.text} - {e} ({full_name}) "
        )


# Получение информации по налоговому вычету
@router.message(StateFilter(SalaryInput.temperature_work), F.text)
async def input_temperature_work(message: Message, state: FSMContext):
    data = await state.get_data()
    salary = restore_salary(await state.get_data())
    user = message.from_user
    full_name = user.full_name
    try:
        salary.temperature_work = message.text
        await state.update_data(salary=salary)
        await state.set_state(SalaryInput.children)
        await message.answer(
                "👨‍👧‍👦 Введите через запятую данные детей на которых производится налоговый вычет в формате:\n"
                "Нет налогового вычета укажите: 0\n\n"
                "Примеры ввода:\n"
                "на 1-го и 2-го: *1,2*\n"
                "на 2-го и 3-го: *2,3*, и т.д.",
                reply_markup=get_back_finish_kb(), parse_mode="Markdown"
        )
        logger.info(
                f"Введено количество детей на налоговый вычет {message.text} ({full_name})"
        )
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
                f"Ошибка ввода количество детей {message.text} - {e} - ({full_name}) "
        )


# Получение информации по алиментам
@router.message(StateFilter(SalaryInput.children), F.text)
async def input_children(message: Message, state: FSMContext):
    data = await state.get_data()
    salary = restore_salary(await state.get_data())
    user = message.from_user
    full_name = user.full_name
    try:
        salary.children = message.text
        await state.update_data(salary=salary)
        await state.set_state(SalaryInput.alimony)
        await message.answer(
                "👨‍👩‍👧‍👧Введите через запятую или одним числом процент по алиментам.\n"
                "Нет алиментов укажите: 0\n\n"
                "Примеры ввода:\n"
                "От одного брака и один ребенок: *25*\n"
                "От одного брака и два ребенка: *33*\n"
                "От одного брака и три ребенка и более: *50*\n"
                "От разных браков: *25,25* или *25,16* или *33,25* и т.п.",
                reply_markup=get_back_finish_kb(), parse_mode="Markdown"
        )
        logger.info(f"Введен процент по алиментам {message.text} ({full_name})")
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
                f"Ошибка ввода алиментов ({message.text}) - {e} - ({full_name})"
        )


# Итоговый вывод
@router.message(StateFilter(SalaryInput.alimony), F.text)
async def input_alimony(message: Message, state: FSMContext):
    data = await state.get_data()
    salary = restore_salary(await state.get_data())
    user = message.from_user
    full_name = user.full_name

    try:
        salary.alimony = message.text
        await state.update_data(salary=salary)

        # Преобразуем в GetDataSalary
        get_salary = GetDataSalary.from_base_salary(salary)

        # Начислено
        calc = CalculationBaseSalary(get_salary)

        result_answer = await calc.calculation_answer()
        result_base_month = await calc.calculation_base_month()
        result_month_quarter = await calc.month_quarter_payment_calculation()

        await message.answer(
                f"✅ Итоговая сумма к выплате: *{result_answer} ₽*\n"
                f"👆 Дополнительно Вам будет выплачено: *{result_base_month} ₽*\n"
                f"в {result_month_quarter}.", parse_mode="Markdown"
        )
        await message.answer(
                f"Вам предоставить полные данные по расчету?\n",
                reply_markup=show_full_result_kb,
        )

        # Переводим в состояние ожидания ответа
        await state.set_state(SalaryInput.show_full_result)

    except ValueError as e:
        await message.answer(f"Ошибка: {e}")


@router.callback_query(
        StateFilter(SalaryInput.show_full_result), F.data == "show_full_result"
)
async def show_full_result_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)  # 🔥 Удаляем кнопки

    data = await state.get_data()
    salary = restore_salary(await state.get_data())

    get_salary = GetDataSalary.from_base_salary(salary)

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

    await callback.message.answer("Подробный расчёт...")
    await callback.message.answer(
            f"НАЧИСЛЕНО:\n"
            f"Оклад за фактическое отработанное время: *{result_base_salary} ₽*\n"
            f"Доплата за работу в ночное время: *{result_night_shifts} ₽*\n"
            f"Премия ежемесячная: *{result_bonus} ₽*\n"
            f"Надбавка за вредные условия труда: *{result_underground} ₽*\n"
            f"Доплата за работу в температуре свыше +26С: *{result_in_temperature} ₽*\n"
            f"Районный коэффициент: *{result_district_allowance} ₽*\n"
            f"Северная надбавка: *{result_north_allowance} ₽*\n"
            f"Налоговый вычет на детей: *{result_deduction_for_children} ₽*\n\n"
            f"✅ ИТОГО НАЧИСЛЕНИЯ: *{result_total_accruals} ₽*\n", parse_mode="Markdown"
    )
    await callback.message.answer(
            f"УДЕРЖАНО:\n"
            f"Налог с начислений (НДФЛ): *{result_withholding_tax} ₽*\n"
            f"Алименты: *{result_alimony} ₽*\n"
            f"✅ ИТОГО К ВЫПЛАТЕ: *{result_answer} ₽*\n"
            f"👆 Дополнительно Вам будет выплачено: *{result_base_month} ₽*\n"
            f"в *{result_month_quarter}.*", parse_mode="Markdown"
    )

    await callback.answer()
    await state.clear()


@router.callback_query(F.data == "go_back")
async def go_back_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)

    current_state_str = await state.get_state()
    current_state = getattr(SalaryInput, current_state_str.split(":")[-1], None)

    if current_state is None:
        await callback.message.answer("❌ Не удалось определить текущее состояние.")
        await callback.answer()
        return

    previous_state = get_previous_state(current_state)

    if previous_state:
        await prompt_for_state(callback.message, state, previous_state)
    else:
        await callback.message.answer("🔙 Невозможно вернуться назад.")

    await callback.answer()
