from decimal import Decimal, ROUND_HALF_UP, getcontext
from salary_dgs.models import GetDataSalary
from salary_dgs.services import CalculationBaseSalary

emp = GetDataSalary()
emp.base_salary = "59300"
emp.month = "февраль"
emp.sum_days = "23"
emp.night_shifts = "1"
emp.evening_shifts = "0"
emp.temperature_work = "0"
emp.children = "2,3"
emp.alimony = "25,50"
answer_base_salary = CalculationBaseSalary(salary_data=emp)
total_accruals = answer_base_salary.calculation_total_accruals()
withholding_tax = answer_base_salary.calculation_withholding_tax()
deduction_for_children = answer_base_salary.calculation_deduction_for_children()

alimony_user = [
    Decimal(x.strip())
    for x in emp.get_alimony().split(",")
    if x.strip().isdigit()
]

deduction = Decimal("0.00")
for i in alimony_user:
    if i == 16:
        deduction += Decimal('1') / Decimal('6')
    if i == 25:
        deduction += Decimal('1') / Decimal('4')
    if i == 33:
        deduction += Decimal('1') / Decimal('3')
    if i == 50:
        deduction += Decimal('1') / Decimal('2')

salary = Decimal(emp.base_salary)
# getcontext().prec = 6
# getcontext().rounding = ROUND_HALF_UP


answer = ((total_accruals - withholding_tax) * deduction).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

print(total_accruals)
print(deduction_for_children)
print(withholding_tax)
print(deduction)
print(answer)
