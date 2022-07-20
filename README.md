# Учебный проект
### Описание
Проект продуктового помощника.

### Cсылка на инструкцию по установке Docker
- Скачать docker с оф.сайта (https://www.docker.com)
- Включить виртуализацию на рабочем компьютере

### Команда для клонирования
Клонируйте репозиторий командой в терминале:
```
git clone https://github.com/ADYason/yamdb_final.git
```
### .env
- SECRET_KEY=Django ключ проекта
- HOSTS = хосты, на которых приложение должно работать
- DB_ENGINE=какую бд мы хотим
- DB_NAME=имя базы(для постгрес)
- POSTGRES_USER=имя пользователя(для постгрес)
- POSTGRES_PASSWORD=пароль (для постгрес)
- DB_HOST=остается db
- DB_PORT=порт 5432
### Запуск приложения в контейнере
```
cd .../foodgram-project-react/infra # Переход к compose файлу
docker-compose up -d --build # Для запуска приложения
docker-compose exec web python manage.py migrate # Миграции для активации бд
docker-compose down -v # Для отключения приложения
```
### Заполнение бд
Через суперюзера и панель администрирования

### Технологии
- Django
- Djangorestframework
- Simple JWT
- Gunicorn
- Nginx
- Postgresql

### Автор
Ярослав Горяинов

### Ссылка на развернутый через docker-compose проект
http://51.250.24.19/