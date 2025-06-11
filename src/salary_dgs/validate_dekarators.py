from functools import wraps


def validate_base_salary(func):
    """Валидация базового оклада"""

    def wrapper(self, value):
        if value == "":
            raise ValueError("Значение не может быть пустым.")
        if not value.isdigit():
            raise ValueError("Значение должно быть числом.")
        return func(self, value)

    return wrapper


def validate_month(month_in_year):  # декоратор с параметром
    """Валидация месяца"""

    def decorator(func):
        def wrapper(self, value):
            if value == "":
                raise ValueError("Значение не может быть пустым.")
            if not value.lower().strip() in month_in_year:
                raise ValueError("Значение должно быть месяцем года.")
            return func(self, value)

        return wrapper

    return decorator


def validate_days_night_evening_temperature(func):
    """Валидация количества дней"""

    def wrapper(self, value):
        if value == "":
            raise ValueError("Значение не может быть пустым.")
        if not value.isdigit():
            raise ValueError("Значение должно быть числом.")
        if not int(value) <= 31:
            raise ValueError("Значение должно быть не больше 31.")
        return func(self, value)

    return wrapper


def validate_evening_shifts(func):  # декоратор с параметром
    """Валидация месяца"""

    def wrapper(self, value):
        # Проверяем, что все необходимые поля заполнены
        if self._sum_days is None:
            raise ValueError("Сначала укажите общее количество дней")

        if self._night_shifts is None:
            raise ValueError("Сначала укажите количество ночных смен")

        # Конвертируем в числа и проверяем
        try:
            sum_days = int(self._sum_days)
            night_shifts = int(self._night_shifts)
            evening_shifts = int(value)
        except (ValueError, TypeError):
            raise ValueError("Все значения должны быть числами")

        # Основная валидация
        if night_shifts + evening_shifts > sum_days:
            raise ValueError(
                f"Сумма ночных ({night_shifts}) и вечерних ({evening_shifts}) смен "
                f"не может превышать общее количество дней ({sum_days})"
            )

        return func(self, value)

    return wrapper


def validate_days_temperature_work(func):
    """Валидация количества дней работы в температуре"""

    def wrapper(self, value):
        if value == "":
            raise ValueError("Значение не может быть пустым.")
        if not value.isdigit():
            raise ValueError("Значение должно быть числом.")
        if not int(value) <= 31:
            raise ValueError("Значение должно быть не больше 31.")

        # Проверяем, что все необходимые поля заполнены
        if self._sum_days is None:
            raise ValueError("Сначала укажите общее количество дней")

        # Конвертируем в числа и проверяем
        # try:
        sum_days = int(self._sum_days)
        temperature_work = int(value)
        # except (ValueError, TypeError):
        #     raise ValueError("Все значения должны быть числами")

        if temperature_work > sum_days:
            raise ValueError(
                f"Количество дней ({temperature_work}) "
                f"работы в температуре не должно превышать общее количество дней ({sum_days})"
            )

        return func(self, value)

    return wrapper


def validate_children(func):
    """Декоратор для валидации ввода количества детей.

    Проверяет:
    - что значение не пустое
    - что ввод состоит из чисел, разделенных запятыми
    - что числа находятся в допустимом диапазоне (1-10)
    - что нет повторяющихся номеров
    - что номера идут последовательно без пропусков
    """

    @wraps(func)
    def wrapper(self, value):
        if not value.strip():
            raise ValueError("Значение не может быть пустым.")

        children = []
        for part in value.split(","):
            part = part.strip()
            if not part.isdigit():
                raise ValueError(
                    f"Некорректное значение '{part}'. Должно быть целое число."
                )

            child_num = int(part)
            # if child_num < 1:
            #     raise ValueError(f"Номер ребенка не может быть меньше 1 (получено {child_num}).")
            if child_num > 10:
                raise ValueError(
                    f"Слишком большой номер ребенка: {child_num}. Максимум 10."
                )

            if child_num in children:
                raise ValueError(f"Номер ребенка {child_num} указан повторно.")

            children.append(child_num)

        # Проверка последовательности
        if len(children) > 1:
            sorted_children = sorted(children)
            for i in range(1, len(sorted_children)):
                if sorted_children[i] != sorted_children[i - 1] + 1:
                    raise ValueError(
                        f"Номера детей должны идти последовательно без пропусков. "
                        f"Обнаружен пропуск между {sorted_children[i - 1]} и {sorted_children[i]}"
                    )

        return func(self, ",".join(map(str, sorted(children))))

    return wrapper


def validate_alimony(func):
    """Декоратор для валидации ввода количества алиментов.

    Проверяет:
    - что значение не пустое
    - что ввод состоит из чисел, разделенных запятыми
    - что числа находятся в допустимом диапазоне (16-70)
    """

    @wraps(func)
    def wrapper(self, value):
        if not value.strip():
            raise ValueError("Значение не может быть пустым.")

        alimony_list = []
        for part in value.split(","):
            part = part.strip()
            if not part.isdigit():
                raise ValueError(
                    f"Некорректное значение '{part}'. Должно быть целое число."
                )

            alimony_num = int(part)
            if alimony_num < 16:
                raise ValueError(f"Слишком маленький процент: {alimony_num}. Минимум 16.")
            if alimony_num > 70:
                raise ValueError(
                    f"Слишком большой процент: {alimony_num}. Максимум 70."
                )

            alimony_list.append(alimony_num)

        return func(self, ",".join(map(str, sorted(alimony_list))))

    return wrapper
