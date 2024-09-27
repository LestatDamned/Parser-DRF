# Используем официальный образ Python на базе Alpine
FROM python:3.12.0-alpine

# Устанавливаем рабочую директорию
WORKDIR /usr/src/app

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Обновляем pip
RUN pip install --upgrade pip

# Копируем файл с зависимостями
COPY requirements.txt /usr/src/app/

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Копируем всё содержимое проекта
COPY . /usr/src/app/

# Выполняем миграции базы данных
#RUN python manage.py migrate
