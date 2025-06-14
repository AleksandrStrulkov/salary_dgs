import asyncio
import os
from dotenv import load_dotenv
from dataclasses import asdict
from aiogram import Router, F, Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from bot.inline_yes_button import show_full_result_kb, back_button_kb, main_menu_kb, show_months_of_years
from bot.states import SalaryInput
from salary_dgs.constant import EN_TO_RU_MONTHS
from \
    salary_dgs.models import BaseSalary, GetDataSalary
from salary_dgs.services import CalculationBaseSalary, logger

# from salary_dgs import logger
router = Router()

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))


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

used_users = set()


def restore_salary(data: dict) -> BaseSalary:
    salary_data = data.get("salary")
    if isinstance(salary_data, BaseSalary):
        return salary_data
    return BaseSalary.from_dict(salary_data)


@router.message(Command("start"))
async def start_handler(message: Message):
    used_users.add(message.from_user.id)
    await message.answer(
        "👋 *Привет!*\n"
        "🚀 Я посчитаю *Вашу зарплату!* Выберите действие:",
        reply_markup=main_menu_kb, parse_mode="Markdown"
    )


@router.message(Command("stats"))
async def stats_handler(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            f"👥 Пользователей воспользовалось ботом: {len(used_users)}"
        )
    else:
        await message.answer("⛔️ Недостаточно прав.")


@router.message(Command("help"))
async def stats_handler(message: Message):
    await message.answer(
        f"*1. ПРЕМИЯ:*\n"
        "От базового оклада - *40%*\n\n"
        "*2. ДОПЛАТА ЗА РАБОТУ В НОЧНОЕ ВРЕМЯ:*\n"
        "От базового оклада за фактически отработанное время - *20%*\n"
        "В ночную смену - *6ч.*\n"
        "В вечернюю смену - *1,3ч.*\n\n"
        "*3. НАДБАВКА ЗА ВРЕДНЫЕ УСЛОВИЯ ТРУДА:*\n"
        "От базового оклада - *4%*\n\n"
        "*4. ДОПЛАТА ЗА РАБОТУ В ВЫРАБОТКАХ С ТЕМПРЕТУРОЙ ВОЗДУХА ОТ +26 ДО +30С:*\n"
        "От базового оклада - *10%*\n\n"
        "*5. РАЙОННЫЙ КОЭФФИЦИЕНТ:*\n"
        "Пункты расчета 1,2,3,4 суммируются,\n"
        "и применяется надбавка от этой суммы - *30%*\n\n"
        "*6. СЕВЕРНАЯ НАДБАВКА:*\n"
        "Пункты расчета 1,2,3,4 суммируются,\n"
        "и применяется надбавка от этой суммы - *50%*\n\n"
        "*7. ОПЛАТА В ДВОЙНОМ РАЗМЕРЕ:*\n"
        "Разница между фактически отработанными днями и нормой\n"
        "рабочего времени за месяц оплачивается в двойном размере.\n"
        "Первая оплата - в месяц расчета со всеми надбавками,\n"
        "Вторая оплата - в расчетный период квартала без надбавок.\n\n"
        "*8. НАЛОГОВЫЙ ВЫЧЕТ НА ДЕТЕЙ:*\n"
        "На первого ребенка - *1400 ₽*\n"
        "На второго ребенка - *1600 ₽*\n"
        "На третьего ребенка и последующих - *6000 ₽*\n"
        "Если на первого ребенка налоговый вычет уже не производится, "
        " то на последующих детей сумма вычета не меняется.\n"
        "Стоит учитывать, что налоговый вычет на детей\n*не является постоянным!*\n"
        "Предельный доход, при получении которого у физических лиц сохраняется право "
        " на получение таких вычетов составляет:\n- *450 000 ₽*", parse_mode="Markdown"
    )


@router.callback_query(F.data == "stop")
async def stop_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("✅ Ввод данных остановлен. Вы можете начать заново.")
    await callback.answer()


# 🟢 Стартовая команда
@router.callback_query(F.data == "start")
async def start_callback(callback: CallbackQuery, state: FSMContext):
    # await state.clear()
    await state.set_data({"salary": BaseSalary()})
    await state.set_state(SalaryInput.base_salary)
    await callback.message.answer("💰 Укажите Ваш оклад:")

    logger.info(f"Команда /start, пользователь")
    logger.info(f"Введен оклад пользователем")
    await callback.answer()


# Получение месяца
@router.message(StateFilter(SalaryInput.base_salary), F.text)
async def input_base_salary(message: Message, state: FSMContext):
    data = await state.get_data()
    salary = restore_salary(await state.get_data())
    try:
        salary.base_salary = message.text
        await state.update_data(salary=salary.to_dict())
        await state.set_state(SalaryInput.month)
        await message.answer("📅 Выберите расчетный месяц:", reply_markup=combined_keyboard)

        logger.info(f"Введен месяц {message.text} пользователем {message.from_user.id}")
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
            f"Ошибка ввода месяца {message.text} пользователем {message.from_user.username}"
        )


@router.callback_query(StateFilter(SalaryInput.month), F.data.startswith("month_"))
async def select_month(callback: CallbackQuery, state: FSMContext):
    en_month = callback.data.replace("month_", "").lower()
    ru_month = EN_TO_RU_MONTHS.get(en_month)

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
        "⏱️ Введите общее количество отработанных или планируемых смен:",
        reply_markup=get_back_finish_kb(),
    )
        logger.info(f"Введено общее количество смен {callback.message.text} пользователем {callback.message.from_user.username}")
    except ValueError as e:
        await callback.message.answer(f"Ошибка: {e}")
        logger.error(
                f"Ошибка ввода ночных смен {callback.message.text} пользователем {callback.message.from_user.username}"
        )


# Получение ночных смен
@router.message(StateFilter(SalaryInput.sum_days), F.text)
async def input_sum_days(message: Message, state: FSMContext):
    data = await state.get_data()
    salary = restore_salary(await state.get_data())
    try:
        salary.sum_days = message.text
        await state.update_data(salary=salary)
        await state.set_state(SalaryInput.night_shifts)
        await message.answer(
            "🌙 Введите количество ночных смен.\n" "Введите 0, если таковых нет:",
            reply_markup=get_back_finish_kb(),
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
    salary = restore_salary(await state.get_data())
    try:
        salary.night_shifts = message.text
        await state.update_data(salary=salary)
        await state.set_state(SalaryInput.evening_shifts)
        await message.answer(
            "🕕 Введите количество вечерних смен.\n" "Введите 0, если таковых нет:",
            reply_markup=get_back_finish_kb(),
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
    salary = restore_salary(await state.get_data())
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
            f"Введено количество смен работы в температуре {message.text} "
            f"пользователем {message.from_user.username}"
        )
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
            f"Ошибка ввода количества смен работы в температуре {message.text} "
            f"пользователем {message.from_user.username} - {e}"
        )


# Получение информации по налоговому вычету
@router.message(StateFilter(SalaryInput.temperature_work), F.text)
async def input_temperature_work(message: Message, state: FSMContext):
    data = await state.get_data()
    salary = restore_salary(await state.get_data())
    try:
        salary.temperature_work = message.text
        await state.update_data(salary=salary)
        await state.set_state(SalaryInput.children)
        await message.answer(
            "👨‍👧‍👦 Введите через запятую данные детей на которых производится налоговый вычет в формате:\n"
            "Нет налогового вычета укажите: 0\n"
            "на 1-го и 2-го: *1,2*\n"
            "на 2-го и 3-го: *2,3*, и т.д.",
            reply_markup=get_back_finish_kb(), parse_mode="Markdown"
        )
        logger.info(
            f"Введено количество детей на налоговый вычет {message.text} "
            f"пользователем {message.from_user.username}"
        )
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")
        logger.error(
            f"Ошибка ввода количество детей {message.text} "
            f"пользователем {message.from_user.username} - {e}"
        )


# Получение информации по алиментам
@router.message(StateFilter(SalaryInput.children), F.text)
async def input_children(message: Message, state: FSMContext):
    data = await state.get_data()
    salary = restore_salary(await state.get_data())
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
    salary = restore_salary(await state.get_data())

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


@router.callback_query(StateFilter(SalaryInput.show_full_result), F.data == "finish")
async def finish_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("✅ Расчёт завершён. Спасибо за использование бота!")
    await callback.answer()
    await state.clear()


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


def get_previous_state(current_state: State) -> State | None:
    try:
        index = step_sequence.index(current_state)
        if index > 0:
            return step_sequence[index - 1]
    except ValueError:
        pass
    return None


def get_back_finish_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="go_back"),
                InlineKeyboardButton(text="⛔ Завершить", callback_data="stop"),
            ]
        ]
    )


combined_keyboard = InlineKeyboardMarkup(
    inline_keyboard=show_months_of_years.inline_keyboard + get_back_finish_kb().inline_keyboard
)


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
