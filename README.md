# Parser DRF

Этот проект представляет собой API для парсинга статей с Habr. 
API реализовано с использованием Django REST Framework (DRF) и асинхронной обработки задач через Celery. 
Проект поддерживает JWT авторизацию, хранение пользовательской истории запросов, результаты парсинга, а также предоставляет Swagger документацию.

## Описание

**Функционал:**
- JWT авторизация
- Асинхронный запуск парсера через Celery
- Хранение истории запросов пользователя
- Хранение результатов парсинга
- Интеграция Swagger для документации API

**Что парсится:**
- Ссылка на статью
- Заголовок
- Текст статьи
- Дата публикации
- Автор и его контактные данные
- Рейтинг статьи
- Количество добавлений в закладки
- 5 самых популярных комментариев

## Стек технологий

- **Django** с **Django REST Framework (DRF)**
- **Celery** для асинхронной обработки задач
- **Redis** как брокер сообщений для Celery
- **Docker** и **Docker Compose** для контейнеризации
- **PostgreSQL** как основная база данных
- **Swagger** для документации API

## Установка
1. **Клонировать репозиторий**:
    ```bash
    git clone https://github.com/LestatDamned/Parser-DRF
    ```

2. **Создайте и активируйте виртуальное окружение**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # для Linux/Mac
    venv\Scripts\activate  # для Windows
    ```

3. **Создать файл .env в корневой директории**: 
    ```
    SECRET_KEY = 'secret_key'
    DEBUG = True
    DJANGO_ALLOWED_HOSTS = 'your_host'
    CSRF_TRUSTED_ORIGINS = 'http://your_host'
    
    SQL_ENGINE="django.db.backends.postgresql"
    SQL_DATABASE="example"
    SQL_USER="example"
    SQL_PASSWORD="password_example"
    SQL_HOST="db"
    SQL_PORT="5432"
    DATABASE="postgres"
    
    INTERNAL_IPS = 'your_host'
    
    ```

4. **Установите зависимости**:
    ```bash
    cd app
    pip install -r requirements.txt
    ```

5. **Запустить Docker Compose**: 
    ```bash
    docker-compose -f docker-compose.prod.yml up --build
    ```

6. **Создать суперпользователя Django**:
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

7. **Проверить работу API**: 
   Откройте браузер и перейдите по адресу [http://localhost:8000/schema/swagger/](http://localhost:8000/schema/swagger/), чтобы ознакомиться с документацией API, предоставляемой Swagger.

8. **Тестирование API**:
   Вы можете использовать Postman для тестирования API, отправляя запросы на конечные точки, указанные в документации.
