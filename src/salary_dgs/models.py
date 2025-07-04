from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass, field

from salary_dgs.constant import MONTHS_IN_YEAR_DAYS
from salary_dgs.validate_dekarators import (
    validate_base_salary,
    validate_month,
    validate_evening_shifts,
    validate_days_night_evening_temperature,
    validate_days_temperature_work,
    validate_children, validate_alimony, validate_night_shifts,
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
    init_count: int = 0

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
    @validate_night_shifts
    def night_shifts(self, value):
        self._night_shifts = value.strip()

    @property
    def evening_shifts(self):
        return self._evening_shifts

    @evening_shifts.setter
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
        self._children = value.strip().replace(".", ",")

    @property
    def alimony(self):
        return self._alimony

    @alimony.setter
    @validate_alimony
    def alimony(self, value):
        self._alimony = value.strip().replace(".", ",")

    def to_dict(self):
        """Преобразовать объект в словарь для сохранения состояния"""
        return {
                "_base_salary": self._base_salary,
                "_month": self._month,
                "_sum_days": self._sum_days,
                "_night_shifts": self._night_shifts,
                "_evening_shifts": self._evening_shifts,
                "_temperature_work": self._temperature_work,
                "_children": self._children,
                "_alimony": self._alimony,
        }

    @classmethod
    def from_dict(cls, data):
        """Создать объект из словаря состояния"""
        return cls(
                _base_salary=data.get("_base_salary"),
                _month=data.get("_month"),
                _sum_days=data.get("_sum_days"),
                _night_shifts=data.get("_night_shifts"),
                _evening_shifts=data.get("_evening_shifts"),
                _temperature_work=data.get("_temperature_work"),
                _children=data.get("_children"),
                _alimony=data.get("_alimony"),
        )


class GetDataSalary(BaseSalary):

    @classmethod
    def from_base_salary(cls, base: BaseSalary):
        return cls(
                _base_salary=base.base_salary,
                _month=base.month,
                _sum_days=base.sum_days,
                _night_shifts=base.night_shifts,
                _evening_shifts=base.evening_shifts,
                _temperature_work=base.temperature_work,
                _children=base.children,
                _alimony=base.alimony,
        )

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
        return self.children.strip().replace(".", ",")

    async def get_alimony(self):
        return self.alimony.strip().replace(".", ",")
