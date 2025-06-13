FROM python:3.12-slim

# Установка зависимостей
WORKDIR /app

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main_bot.py"]