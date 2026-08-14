# 1. Используем легкий базовый образ Python 3.11 на основе Linux Alpine/Slim
FROM python:3.11-slim

# 2. Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# 3. Отключаем буферизацию вывода Python (чтобы логи сразу попадали в консоль Docker)
ENV PYTHONUNBUFFERED=1

# 4. Копируем список зависимостей и устанавливаем их
# (Делаем это ДО копирования кода, чтобы Docker кэшировал слой с библиотеками)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем исходный код приложения
COPY app ./app

# 6. Открываем порт 8000
EXPOSE 8000

# 7. Команда запуска сервера при старте контейнера
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]