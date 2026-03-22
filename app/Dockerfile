# Используем базовый образ с Python 3.10
FROM python:3.10-slim

# Установка зависимостей
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=app.settings

# Установка необходимых пакетов
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочего каталога
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip setuptools
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения
COPY . .

# Открываем порт для сервера
EXPOSE 8000

# Команда для запуска вашего Django проекта
 CMD ["gunicorn", "--bind", "0.0.0.0:8000", "/app/app.wsgi:application"]