FROM python:3.12.0-slim

# Устанавливаем рабочую директорию
WORKDIR /Hatico-technic

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
COPY . .

# Выполняем миграции перед запуском бота
ENTRYPOINT ["sh", "-c", "alembic upgrade head && python3 -m bot.main"]
