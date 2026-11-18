# МАСТЕРСКАЯ — Маркетплейс изделий ручной работы

## Структура проекта
- `manage.py` — запуск сервера и команд управления Django.
- `project/` — общие настройки проекта (`settings.py`, главный `urls.py`).
- `app/` — основное приложение магазина (`models.py`, `views.py`, `forms.py`, `urls.py`, `admin.py`).
- `app/templates/` — HTML-шаблоны страниц с наследованием от `base.html`.
- `app/static/` — стили `style.css`, скрипты `main.js` и изображения.

## Запуск
1. `pip install django pillow`
2. `python manage.py migrate`
3. `python manage.py seed`
4. `python manage.py runserver`
