from salary_dgs.constant import *
from decimal import Decimal, ROUND_HALF_UP, getcontext

from salary_dgs.models import GetDataSalary
import asyncio


class CalculationBaseSalary:

    def __init__(self, salary_data: GetDataSalary):
        self.salary_data = salary_data

    async def calculation_base_salary(self) -> Decimal:
        """Расчет оклада по рабочим дням"""
        base_salary = await self.salary_data.get_base_salary()
        month = await self.salary_data.get_month()
        normal_days_in_month = Decimal(MONTHS_IN_YEAR_DAYS.get(month)).quantize(
            Decimal("0.01")
        )
        sum_days = await self.salary_data.get_sum_days()
        return (base_salary * sum_days / normal_days_in_month).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    async def calculation_night_shifts(self) -> Decimal:
        """Расчет доплаты за работу в ночное время"""
        base_salary = await self.salary_data.get_base_salary()
        month = await self.salary_data.get_month()
        night_days = await self.salary_data.get_night_shifts()
        evening_days = await self.salary_data.get_evening_shifts()

        monthly_hours_norm = Decimal(MONTHS_IN_YEAR_HOURS[month])
        night_hours_per_day = Decimal(FACTORS["Ночные 1 смена"])
        evening_hours_per_day = Decimal(FACTORS["Ночные 3 смена"])
        night_pay_percent = Decimal(FACTORS["Процент оплаты ночных"])

        # Расчет общего количества часов
        total_night_hours = night_days * night_hours_per_day
        total_evening_hours = evening_days * evening_hours_per_day

        # Расчет оплаты
        hourly_rate = base_salary / monthly_hours_norm

        night_payment = (
            hourly_rate * total_night_hours if night_days else Decimal("0.00")
        )
        evening_payment = (
            hourly_rate * total_evening_hours if evening_days else Decimal("0.00")
        )

        total_payment = (night_payment + evening_payment) * night_pay_percent / 100

        return total_payment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    async def calculation_underground(self) -> Decimal:
        """Расчет надбавки за работу в подземных условиях"""
        base_salary = await self.calculation_base_salary()
        surcharge_for_underground = Decimal(FACTORS.get("Подземные условия")).quantize(
            Decimal("0.01")
        )
        return (base_salary * surcharge_for_underground / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    async def calculation_bonus(self) -> Decimal:
        """Расчет премии"""
        base_salary = await self.calculation_base_salary()
        calculation_underground = await self.calculation_underground()
        calculation_night_shifts = await self.calculation_night_shifts()
        total_amount = base_salary + calculation_underground + calculation_night_shifts
        bonus = Decimal(FACTORS.get("Премия")).quantize(Decimal("0.01"))
        return (total_amount * bonus / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    async def calculation_base(self) -> Decimal:
        """Расчет базовой суммы"""
        base_salary = await self.calculation_base_salary()
        calculation_bonus = await self.calculation_bonus()
        calculation_underground = await self.calculation_underground()
        calculation_night_shifts = await self.calculation_night_shifts()
        return (
            base_salary
            + calculation_bonus
            + calculation_underground
            + calculation_night_shifts
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    async def calculation_district_allowance(self) -> Decimal:
        """Расчет районной надбавки"""
        calculation_base = await self.calculation_base()
        district_allowance = Decimal(FACTORS["Районный коэффициент"])
        return (calculation_base * district_allowance / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    async def calculation_north_allowance(self) -> Decimal:
        """Расчет северной надбавки"""
        calculation_base = await self.calculation_base()
        district_allowance = Decimal(FACTORS["Северная надбавка"])
        return (calculation_base * district_allowance / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    async def calculation_working_in_temperature(self) -> Decimal:
        """Расчет надбавки за работу в условиях повышенной температуры"""
        base_salary = await self.salary_data.get_base_salary()
        month = await self.salary_data.get_month()
        working_in_temperature = await self.salary_data.get_temperature_work()

        monthly_rate_hours = Decimal(MONTHS_IN_YEAR_HOURS[month])
        surcharge_for_temperature = Decimal(FACTORS["Доплата за температуру"])

        converted_days_in_hours = working_in_temperature * Decimal('5')
        pay_per_hour = base_salary / monthly_rate_hours
        without_interest = converted_days_in_hours * pay_per_hour

        return (without_interest * surcharge_for_temperature / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    async def calculation_total_accruals(self) -> Decimal:
        """Расчет общей суммы начислений"""
        return (
            await self.calculation_base()
            + await self.calculation_district_allowance()
            + await self.calculation_north_allowance()
            + await self.calculation_working_in_temperature()
        )

    async def calculation_deduction_for_children(self) -> Decimal:
        """Расчет налогового вычета на детей"""
        children = [
            Decimal(x.strip())
            for x in (await self.salary_data.get_children()).split(",")
            if x.strip().isdigit()
        ]
        total_accruals = await self.calculation_total_accruals()

        deduction = Decimal("0")
        if 1 in children:
            deduction += Decimal("1400")
        if 2 in children:
            deduction += Decimal("2800")  # 2800 total for first two
        if 3 in children:
            deduction += Decimal("6000")  # 6000 total for first three

            # Для 4го и последующих детей также +3000 каждый
        extra_children = len([x for x in children if x >= 4])
        deduction += extra_children * Decimal("6000")

        return (deduction * Decimal("0.13")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    async def calculation_withholding_tax(self) -> Decimal:
        """ Расчет подоходного налога"""
        total_accruals = await self.calculation_total_accruals()
        deduction_for_children = await self.calculation_deduction_for_children()
        withholding_tax = Decimal(FACTORS["НДФЛ"])
        if deduction_for_children == Decimal("0.00"):
            return (total_accruals * withholding_tax / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return (total_accruals * withholding_tax / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) - \
            deduction_for_children

    async def calculation_alimony(self) -> Decimal:
        """Расчет алиментов на детей

        Возвращает:
            Decimal: Сумма алиментов, округленная до копеек
        """
        # Рассчитываем НДФЛ и общие начисления
        withholding_tax = await self.calculation_withholding_tax()
        total_accruals = await self.calculation_total_accruals()

        # Получаем и обрабатываем ввод по алиментам
        alimony_input = await self.salary_data.get_alimony()
        alimony_rates = {
                16: Decimal('1') / Decimal('6'),  # 1/6 ≈ 16.67%
                25: Decimal('1') / Decimal('4'),  # 25%
                33: Decimal('1') / Decimal('3'),  # ≈33.33%
                50: Decimal('1') / Decimal('2')  # 50%
        }

        # Рассчитываем общий процент алиментов
        total_deduction = Decimal('0.00')
        for rate in filter(str.isdigit, map(str.strip, alimony_input.split(','))):
            rate_int = int(rate)
            if rate_int in alimony_rates:
                total_deduction += alimony_rates[rate_int]

        # Вычисляем сумму алиментов от "чистой" зарплаты
        net_salary = total_accruals - withholding_tax
        alimony_amount = (net_salary * total_deduction).quantize(
                Decimal('0.01'),
                rounding=ROUND_HALF_UP
        )

        return alimony_amount

    async def calculation_answer(self) -> Decimal:
        """Формирование итоговой суммы
        """
        total_accruals = await self.calculation_total_accruals()
        withholding_tax = await self.calculation_withholding_tax()
        alimony = await self.calculation_alimony()

        return total_accruals - withholding_tax - alimony

    async def calculation_base_month(self) -> Decimal:
        """Расчет квартальной доплаты за переработку"""
        base_salary = await self.calculation_base_salary()
        salary = await self.salary_data.get_base_salary()

        return (base_salary - salary).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    async def month_quarter_payment_calculation(self) -> str:
        """Определяет месяц выплаты за переработку (в конце квартала)"""
        quarter_to_payment = {
                "декабрь": "март",
                "январь": "март",
                "февраль": "март",
                "март": "июнь",
                "апрель": "июнь",
                "май": "июнь",
                "июнь": "сентябрь",
                "июль": "июнь",
                "август": "сентябрь",
                "сентябрь": "декабрь",
                "октябрь": "декабрь",
                "ноябрь": "декабрь"
        }

        month = await self.salary_data.get_month()
        return quarter_to_payment.get(month, "неизвестный месяц")
