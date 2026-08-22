# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные зависимости для сборки pyswisseph и других пакетов
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта в контейнер
COPY . .

# Создаем папку для данных пользователей
RUN mkdir -p /app/data/user_data

# Открываем порт, который будет слушать приложение
EXPOSE 3000

# Команда для запуска приложения
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "3000"]