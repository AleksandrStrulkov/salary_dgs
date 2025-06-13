from functools import wraps


def validate_base_salary(func):
    """Валидация базового оклада"""

    def wrapper(self, value):
        if value == "":
            raise ValueError("Значение не может быть пустым.")
        if not value.isdigit():
            raise ValueError(f"Некорректное значение ({value}), ожидается число.")
        return func(self, value)

    return wrapper


def validate_month(month_in_year):  # декоратор с параметром
    """Валидация месяца"""

    def decorator(func):
        def wrapper(self, value):
            if value == "":
                raise ValueError("Значение не может быть пустым.")
            if not value.lower().strip() in month_in_year:
                raise ValueError(f"Некорректное значение ({value}), ожидается месяц года.")
            return func(self, value)

        return wrapper

    return decorator


def validate_days_night_evening_temperature(func):
    """Валидация количества дней"""

    def wrapper(self, value):
        if value == "":
            raise ValueError("Значение не может быть пустым.")
        if not value.isdigit():
            raise ValueError(f"Некорректное значение ({value}), ожидается число.")
        if not int(value) <= 31:
            raise ValueError("Значение должно быть не больше - 31.")
        return func(self, value)

    return wrapper


def validate_night_shifts(func):  # декоратор с параметром
    """Валидация ночных смен"""

    def wrapper(self, value):
        # Конвертируем в числа и проверяем
        if value == "":
            raise ValueError("Значение не может быть пустым.")
        if not value.isdigit():
            raise ValueError(f"Некорректное значение ({value}), ожидается число.")

        sum_days = int(self._sum_days)
        night_shifts = int(value)

        # Основная валидация
        if night_shifts > sum_days:
            raise ValueError(
                    f"Количество ночных смен ({night_shifts})\n"
                    f"не может превышать общее количество дней ({sum_days})"
            )

        return func(self, value)

    return wrapper


def validate_evening_shifts(func):  # декоратор с параметром
    """Валидация вечерних смен"""

    def wrapper(self, value):
        # Конвертируем в числа и проверяем
        if value == "":
            raise ValueError("Значение не может быть пустым.")
        if not value.isdigit():
            raise ValueError(f"Некорректное значение ({value}), ожидается число.")

        sum_days = int(self._sum_days)
        night_shifts = int(self._night_shifts)
        evening_shifts = int(value)

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
            raise ValueError(f"Некорректное значение ({value}), ожидается число.")
        if not int(value) <= 31:
            raise ValueError("Значение должно быть не больше 31.")

        # Конвертируем в числа и проверяем
        sum_days = int(self._sum_days)
        temperature_work = int(value)

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

        value_repl = value.strip().replace(".", ",")

        children = []
        for part in value_repl.split(","):
            part = part.strip()
            if not part.isdigit():
                raise ValueError(
                        f"Некорректное значение ({part}). Должно быть целое число."
                )

            child_num = int(part)
            # if child_num < 1:
            #     raise ValueError(f"Номер ребенка не может быть меньше 1 (получено {child_num}).")
            if child_num > 10:
                raise ValueError(
                        f"Расчет позволяет ввести не более 10 детей. Получено: ({len(children) + 1})."
                )

            if child_num in children:
                raise ValueError(f"Последовательность детей ({child_num}) указано повторно.")

            children.append(child_num)

        # Проверка последовательности
        if len(children) > 1:
            sorted_children = sorted(children)
            for i in range(1, len(sorted_children)):
                if sorted_children[i] != sorted_children[i - 1] + 1:
                    raise ValueError(
                            f"Не соблюдается последовательность детей. "
                            f"Обнаружен пропуск между ({sorted_children[i - 1]}) и ({sorted_children[i]})"
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

        value_repl = value.strip().replace(".", ",")
        alimony_options = [16, 25, 33, 70]

        alimony_list = []
        for part in value_repl.split(","):
            part = part.strip()
            if not part.isdigit():
                raise ValueError(
                        f"Некорректное значение ({part}). Должно быть число."
                )

            alimony_num = int(part)
            if alimony_num != 0:
                if alimony_num < 16:
                    raise ValueError(f"Слишком маленький процент: ({alimony_num}). Минимум 16.")
                if alimony_num > 70:
                    raise ValueError(
                            f"Слишком большой процент: ({alimony_num}). Максимум 70."
                    )
                if alimony_num not in alimony_options:
                    raise ValueError(
                            f"Некорректный процент ({alimony_num}). "
                            f"Допустимые значения: {alimony_options}."
                    )

            alimony_list.append(alimony_num)

        return func(self, ",".join(map(str, sorted(alimony_list))))

    return wrapper
