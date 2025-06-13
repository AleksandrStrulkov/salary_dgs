from salary_dgs.cache_decorator import cache_result
from salary_dgs.constant import *
from decimal import Decimal, ROUND_HALF_UP, getcontext
import logging
from salary_dgs.models import GetDataSalary
import asyncio

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s",
        handlers=[
                logging.FileHandler("services.log", encoding="utf-8"),  # Логи в файл
                logging.StreamHandler(),  # Логи в консоль (можно убрать)
        ],
)

logger = logging.getLogger(__name__)


class CalculationBaseSalary:

    def __init__(self, salary_data: GetDataSalary):
        self.salary_data = salary_data
        self._cache = {}

    @cache_result
    async def calculation_base_salary(self) -> Decimal:
        """Расчет оклада по рабочим дням"""
        base_salary = await self.salary_data.get_base_salary()  # Базовый оклад по месячной норме выходов
        month = await self.salary_data.get_month()  # Месяц расчета
        sum_days = await self.salary_data.get_sum_days()  # Всего выходов в месяц расчета

        normal_days_in_month = Decimal(MONTHS_IN_YEAR_DAYS[month])  # Норма выходов в месяце расчета

        result = (base_salary * sum_days / normal_days_in_month).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        logger.info(f"Расчет оклада по рабочим дням {base_salary} * {sum_days} / {normal_days_in_month} = {result}")
        return result

    @cache_result
    async def calculation_night_shifts(self) -> Decimal:
        """Расчет доплаты за работу в ночное время"""
        base_salary = await self.salary_data.get_base_salary()  # Базовый оклад по месячной норме выходов
        month = await self.salary_data.get_month()  # Месяц расчета
        night_days = await self.salary_data.get_night_shifts()  # Всего ночных смен
        evening_days = await self.salary_data.get_evening_shifts()  # Всего вечерних смен

        monthly_hours_norm = Decimal(MONTHS_IN_YEAR_HOURS[month])  # Норма часов в месяце расчета
        night_hours_per_day = Decimal(FACTORS["Ночные 1 смена"])  # Часов в ночной смене
        evening_hours_per_day = Decimal(FACTORS["Ночные 3 смена"])  # Часов в вечерней смене
        night_pay_percent = Decimal(FACTORS["Процент оплаты ночных"])  # Процент оплаты за ночные смены

        # Расчет общего количества часов
        total_night_hours = night_days * night_hours_per_day
        total_evening_hours = evening_days * evening_hours_per_day

        # Расчет оплаты
        hourly_rate = base_salary / monthly_hours_norm

        night_payment = (
            hourly_rate * total_night_hours if night_days else Decimal("0.00")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        evening_payment = (
            hourly_rate * total_evening_hours if evening_days else Decimal("0.00")
        )

        total_payment = (night_payment + evening_payment) * night_pay_percent / 100

        logger.info(f"Расчет доплаты за работу в ночное время {night_payment}+"
                    f"{evening_payment} * {night_pay_percent} / 100 = {total_payment}")
        return total_payment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @cache_result
    async def calculation_underground(self) -> Decimal:
        """Расчет надбавки за работу в подземных условиях"""
        base_salary = await self.calculation_base_salary()  # Расчет оклада по рабочим дням
        surcharge_for_underground = Decimal(FACTORS["Подземные условия"])

        result = (base_salary * surcharge_for_underground / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        logger.info(
            f"Расчет надбавки за работу в подземных условиях {base_salary} * "
            f"{surcharge_for_underground} / 100 = {result}"
            )
        return result

    @cache_result
    async def calculation_bonus(self) -> Decimal:
        """Расчет премии"""
        base_salary = await self.calculation_base_salary()  # Расчет оклада по рабочим дням
        calculation_underground = await self.calculation_underground()  # Расчет надбавки за работу в подземных условиях
        calculation_night_shifts = await self.calculation_night_shifts()  # Расчет доплаты за работу в ночное время

        # Сумма с которой необходимо посчитать премию
        total_amount = base_salary + calculation_underground + calculation_night_shifts

        bonus = Decimal(FACTORS["Премия"])  # Процент премии

        result = (total_amount * bonus / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        logger.info(f"Расчет премии {total_amount} * {bonus} / 100 = {result}")
        return result

    @cache_result
    async def calculation_working_in_temperature(self) -> Decimal:
        """Расчет надбавки за работу в условиях повышенной температуры"""
        base_salary = await self.salary_data.get_base_salary()  # Базовый оклад по месячной норме выходов
        month = await self.salary_data.get_month()  # Месяц расчета
        working_in_temperature = await self.salary_data.get_temperature_work()  # Всего выходов в температуре

        monthly_rate_hours = Decimal(MONTHS_IN_YEAR_HOURS[month])  # Норма часов в месяце расчета
        surcharge_for_temperature = Decimal(FACTORS["Доплата за температуру"])  # Процент надбавки за температуру

        converted_days_in_hours = working_in_temperature * Decimal('5')  # Конвертация дней в часы

        # Расчет оплаты за один час
        pay_per_hour = base_salary / monthly_rate_hours
        # Расчет общей суммы оплаты за все ночные часы
        without_interest = (converted_days_in_hours * pay_per_hour).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        result = (without_interest * surcharge_for_temperature / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        logger.info(f"Расчет надбавки за температуру {without_interest} / {surcharge_for_temperature} / 100 = {result}")
        return result

    @cache_result
    async def calculation_base(self) -> Decimal:
        """Расчет базовой суммы"""
        base_salary = await self.calculation_base_salary()  # Расчет оклада по рабочим дням
        calculation_bonus = await self.calculation_bonus()  # Расчет премии
        calculation_underground = await self.calculation_underground()  # Расчет надбавки за работу в подземных условиях
        calculation_night_shifts = await self.calculation_night_shifts()  # Расчет доплаты за работу в ночное время
        calculation_working_in_temperature = await self.calculation_working_in_temperature()  # Расчет надбавки за t

        result = (
            base_salary
            + calculation_bonus
            + calculation_underground
            + calculation_night_shifts
            + calculation_working_in_temperature
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        logger.info(f"Расчет базовой суммы "
                    f"{base_salary}"
                    f"+{calculation_bonus}"
                    f"+{calculation_underground}+"
                    f"{calculation_night_shifts}"
                    f"+{calculation_working_in_temperature} = {result}"
                    )
        return result

    @cache_result
    async def calculation_district_allowance(self) -> Decimal:
        """Расчет районной надбавки"""
        calculation_base = await self.calculation_base()  # Расчет базовой суммы
        district_allowance = Decimal(FACTORS["Районный коэффициент"])  # Процент районной надбавки

        result = (calculation_base * district_allowance / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        logger.info(f"Расчет районной надбавки {calculation_base} * {district_allowance} / 100 = {result}")
        return result

    @cache_result
    async def calculation_north_allowance(self) -> Decimal:
        """Расчет северной надбавки"""
        calculation_base = await self.calculation_base()  # Расчет базовой суммы
        district_allowance = Decimal(FACTORS["Северная надбавка"])  # Процент северной надбавки

        result = (calculation_base * district_allowance / 100).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        logger.info(f"Расчет северной надбавки {calculation_base} * {district_allowance} / 100 = {result}")
        return result

    @cache_result
    async def calculation_total_accruals(self) -> Decimal:
        """Расчет общей суммы начислений"""

        result = (
            await self.calculation_bonus()
            + await self.calculation_underground()
            + await self.calculation_base_salary()
            + await self.calculation_night_shifts()
            + await self.calculation_district_allowance()
            + await self.calculation_north_allowance()
            + await self.calculation_working_in_temperature()
        )

        logger.info(f"Расчет общей суммы начислений"
                    f"+ {await self.calculation_bonus()}"
                    f"+ {await self.calculation_underground()}"
                    f"+ {await self.calculation_base_salary()}"
                    f"+ {await self.calculation_night_shifts()}"
                    f"+ {await self.calculation_district_allowance()}"
                    f"+ {await self.calculation_north_allowance()}"
                    f"+ {await self.calculation_working_in_temperature()} = {result}")
        return result

    @cache_result
    async def calculation_deduction_for_children(self) -> Decimal:
        """Расчет налогового вычета на детей"""
        children = [
            Decimal(x.strip())
            for x in (await self.salary_data.get_children()).split(",")
            if x.strip().isdigit()
        ]
        total_accruals = await self.calculation_total_accruals()  # Расчет общей суммы начислений

        base_tax = Decimal(FACTORS["НДФЛ"])  # Процент налога

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

        children_raw = await self.salary_data.get_children()

        result = (deduction * base_tax / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if not children_raw:
            return Decimal("0.00")
        logger.info(f"Расчет налогового вычета на детей {deduction} * {base_tax} / 100 = {result}")
        return result

    @cache_result
    async def calculation_withholding_tax(self) -> Decimal:
        """ Расчет подоходного налога"""
        total_accruals = await self.calculation_total_accruals()  # Расчет общей суммы начислений
        deduction_for_children = await self.calculation_deduction_for_children()  # Расчет налогового вычета на детей
        withholding_tax = Decimal(FACTORS["НДФЛ"])  # Процент налога

        result_zero = (total_accruals * withholding_tax / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        result = (total_accruals * withholding_tax / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) - \
            deduction_for_children

        if deduction_for_children == Decimal("0.00"):
            logger.info(f"Расчет подоходного налога {total_accruals} * {withholding_tax} / 100 = {result_zero}")
            return result_zero
        logger.info(f"Расчет подоходного налога {total_accruals} * {withholding_tax} / 100 - {deduction_for_children} = {result}")
        return result

    @cache_result
    async def calculation_alimony(self) -> Decimal:
        """Расчет алиментов на детей

        Возвращает:
            Decimal: Сумма алиментов, округленная до копеек
        """
        # Рассчитываем НДФЛ и общие начисления
        withholding_tax = await self.calculation_withholding_tax()  # Расчет подоходного налога
        total_accruals = await self.calculation_total_accruals()  # Расчет общей суммы начислений

        # Получаем и обрабатываем ввод по алиментам
        alimony_input = await self.salary_data.get_alimony()  # Получение алиментов
        alimony_rates = {
                16: Decimal('1') / Decimal('6'),  # 1/6 ≈ 16.67%
                25: Decimal('1') / Decimal('4'),  # 25%
                33: Decimal('1') / Decimal('3'),  # ≈33.33%
                50: Decimal('1') / Decimal('2')  # 50%
        }

        # Рассчитываем общий процент алиментов
        total_deduction = Decimal('0.00').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
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

        alimony_raw = await self.salary_data.get_children()
        if not alimony_raw:
            return Decimal("0.00")
        logger.info(f"Расчет алиментов на детей {net_salary} * {total_deduction} = {alimony_amount}")
        return alimony_amount

    @cache_result
    async def calculation_answer(self) -> Decimal:
        """Формирование итоговой суммы
        """
        total_accruals = await self.calculation_total_accruals()  # Расчет общей суммы начислений
        withholding_tax = await self.calculation_withholding_tax()  # Расчет подоходного налога
        alimony = await self.calculation_alimony()  # Расчет алиментов на детей

        result = total_accruals - withholding_tax - alimony
        logger.info(f"Расчет итоговой суммы {total_accruals} - {withholding_tax} - {alimony} = {result}")
        return result

    @cache_result
    async def calculation_base_month(self) -> Decimal:
        """Расчет квартальной доплаты за переработку"""
        base_salary = await self.calculation_base_salary()  # Расчет базовой суммы
        salary = await self.salary_data.get_base_salary()  # Получение оклада

        result = (base_salary - salary).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        logger.info(f"Расчет квартальной доплаты за переработку {base_salary} - {salary} = {result}")
        return result

    async def month_quarter_payment_calculation(self) -> str:
        """Определяет месяц выплаты за переработку (в конце квартала)"""
        quarter_to_payment = {
                "январь": "апреле текущего года",
                "февраль": "апреле текущего года",
                "март": "апреле текущего года",
                "апрель": "июле текущего года",
                "май": "июле текущего года",
                "июнь": "июле текущего года",
                "июль": "октябре текущего года",
                "август": "октябре текущего года",
                "сентябрь": "октябре текущего года",
                "октябрь": "январе следующего года",
                "ноябрь": "январе следующего года",
                "декабрь": "январе следующего года"
        }

        month = await self.salary_data.get_month()  # Получение месяца

        logger.info(f"Определяем месяц выплаты за переработку {month} -> {quarter_to_payment.get(month)}")
        return quarter_to_payment.get(month, "неизвестный месяц")
