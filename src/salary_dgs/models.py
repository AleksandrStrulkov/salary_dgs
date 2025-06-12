from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field

from salary_dgs.constant import MONTHS_IN_YEAR_DAYS
from salary_dgs.validate_dekarators import (
    validate_base_salary,
    validate_month,
    validate_evening_shifts,
    validate_days_night_evening_temperature,
    validate_days_temperature_work,
    validate_children, validate_alimony,
)


@dataclass
class BaseSalary:
    _base_salary: str = None
    _month: str = None
    _sum_days: str = None
    _night_shifts: str = None
    _evening_shifts: str = None
    _temperature_work: str = None
    _children: str = None
    _alimony: str = None

    @property
    def base_salary(self):
        return self._base_salary

    @base_salary.setter
    @validate_base_salary
    def base_salary(self, value):
        self._base_salary = value.strip()

    @property
    def month(self):
        return self._month

    @month.setter
    @validate_month(MONTHS_IN_YEAR_DAYS)
    def month(self, value):
        self._month = value.strip().lower()

    @property
    def sum_days(self):
        return self._sum_days

    @sum_days.setter
    @validate_days_night_evening_temperature
    def sum_days(self, value):
        self._sum_days = value.strip()

    @property
    def night_shifts(self):
        return self._night_shifts

    @night_shifts.setter
    @validate_days_night_evening_temperature
    def night_shifts(self, value):
        self._night_shifts = value.strip()

    @property
    def evening_shifts(self):
        return self._evening_shifts

    @evening_shifts.setter
    @validate_days_night_evening_temperature
    @validate_evening_shifts
    def evening_shifts(self, value):
        self._evening_shifts = value.strip()

    @property
    def temperature_work(self):
        return self._temperature_work

    @temperature_work.setter
    @validate_days_temperature_work
    def temperature_work(self, value):
        self._temperature_work = value.strip()

    @property
    def children(self):
        return self._children

    @children.setter
    @validate_children
    def children(self, value):
        self._children = value.strip()

    @property
    def alimony(self):
        return self._alimony

    @alimony.setter
    @validate_alimony
    def alimony(self, value):
        self._alimony = value.strip()


class GetDataSalary(BaseSalary):
    async def get_base_salary(self):
        return Decimal(self.base_salary)

    async def get_month(self):
        return self.month

    async def get_sum_days(self):
        return Decimal(self.sum_days).quantize(Decimal("0.01"))

    async def get_night_shifts(self):
        return Decimal(self.night_shifts).quantize(Decimal("0.01"))

    async def get_evening_shifts(self):
        return Decimal(self.evening_shifts).quantize(Decimal("0.01"))

    async def get_sum_evening_shifts(self):
        return Decimal(self.evening_shifts).quantize(Decimal("0.01"))

    async def get_temperature_work(self):
        return Decimal(self.temperature_work).quantize(Decimal("0.01"))

    async def get_children(self):
        return self.children

    async def get_alimony(self):
        return self.alimony
