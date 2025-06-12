from salary_dgs.models import GetDataSalary
from salary_dgs.services import CalculationBaseSalary
import asyncio


async def main():
    emp = GetDataSalary()
    print("Пожалуйста, введите следующие данные:")
    while emp.base_salary is None:
        try:
            emp.base_salary = input("Введите ваш оклад: ").strip()
            print(await emp.get_base_salary())
            print("Данные оклада приняты")
            break
        except ValueError as error:
            print(f"Ошибка: {error}")

    while emp.month is None:
        try:
            emp.month = input("Введите месяц: ").strip().lower()
            print(await emp.get_month())
            print("Данные месяца приняты")
            break
        except ValueError as error:
            print(f"Ошибка: {error}")

    while emp.sum_days is None:
        try:
            emp.sum_days = input("Введите количество дней: ").strip()
            print(await emp.get_sum_days())
            print("Данные количества дней приняты")
            break
        except ValueError as error:
            print(f"Ошибка: {error}")

    while emp.night_shifts is None:
        try:
            emp.night_shifts = input("Введите количество ночных смен: ").strip()
            print(await emp.get_night_shifts())
            print("Данные количества смен приняты")
            break
        except ValueError as error:
            print(f"Ошибка: {error}")

    while emp.evening_shifts is None:
        try:
            emp.evening_shifts = input("Введите количество вечерних смен: ").strip()
            print(await emp.get_evening_shifts())
            print("Данные количества смен приняты")
            break
        except ValueError as error:
            print(f"Ошибка: {error}")

    while emp.temperature_work is None:
        try:
            emp.temperature_work = input(
                    "Введите количество смен работы в температуре свыше 26 градусов: "
            ).strip()
            print(await emp.get_temperature_work())
            print("Данные температуры приняты")
            break
        except ValueError as error:
            print(f"Ошибка: {error}")

    while emp.children != "0":
        try:
            emp.children = input(
                    "Введите через запятую количество и на каких детей получаете налоговый вычет.\n"
                    "Например:\n"
                    "Нет налогового вычета укажите: 0\n"
                    "на 1-го и 2-го: 1,2\n"
                    "на 2-го и 3-го: 2,3: "
            ).strip()
            print(await emp.get_children())
            print("Данные детей приняты")
            break
        except ValueError as error:
            print(f"Ошибка: {error}")

    while emp.alimony != "0":
        try:
            emp.alimony = input(
                    "Введите через запятую количество алиментов.\n"
                    "Например:\n"
                    "От одного брака: 25 или 33 или 50\n"
                    "От разных браков: 25,25 или 25,16 или 33,25 или 50,25 и т.д.: "
            ).strip()
            print(await emp.get_alimony())
            print("Данные алиментов детей приняты")
            break
        except ValueError as error:
            print(f"Ошибка: {error}")

    salary = await emp.get_base_salary()
    night_shifts = await emp.get_night_shifts()

    answer_base_salary = CalculationBaseSalary(salary_data=emp)

    print(f"Голый оклад: {await answer_base_salary.calculation_base_salary()}")
    print(f"Оплата за ночные смены: {await answer_base_salary.calculation_night_shifts()}")
    print(f"Доплата за вредность: {await answer_base_salary.calculation_underground()}")
    print(f"Премия: {await answer_base_salary.calculation_bonus()}")
    print(f"Оклад с начислениями: {await answer_base_salary.calculation_base()}")
    print(f"Районный коэффициент: {await answer_base_salary.calculation_district_allowance()}")
    print(f"Северная надбавка: {await answer_base_salary.calculation_north_allowance()}")
    print(f"Оплата в температуре: {await answer_base_salary.calculation_working_in_temperature()}")
    print(f"Общие начисления: {await answer_base_salary.calculation_total_accruals()}")
    print(f"Налоговый вычет: {await answer_base_salary.calculation_deduction_for_children()}")
    print(f"Подоходный налог: {await answer_base_salary.calculation_withholding_tax()}")
    print(f"Выплата по алиментам: {await answer_base_salary.calculation_alimony()}")
    print(f"Ваша итоговая зарплата: {await answer_base_salary.calculation_answer()}")
    # print(f"Ваша доплата за переработку: {answer_base_salary.calculation_base_month()}")
    print(
        f"Доп.сумму за переработку: {await answer_base_salary.calculation_base_month()}\n"
        f"вы получите в конце квартала, месяц: "
        f"{(await answer_base_salary.month_quarter_payment_calculation()).capitalize()}"
        )
    print(f"переменные районной надбавки: {await answer_base_salary.calculation_district_allowance()}")

if __name__ == "__main__":
    asyncio.run(main())
