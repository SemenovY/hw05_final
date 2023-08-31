[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=ffffff&color=043A6B)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=ffffff&color=043A6B)](https://www.Django.org/)

________
# Социальная сеть для публикации личных дневников

## Технологии
* Python
* Django
* Pillow
* pytest

### Описание
После регистрации пользователь может создавать посты, подписываться на авторов
и комментировать их записи.
Если зайти на страницу автора, то можно посмотреть все его записи.
После публикации каждая запись доступна на странице автора.

## Инструкция по развёртыванию проекта

* Клонировать репозиторий и перейти в него в командной строке
```
git clone git@github.com:SemenovY/hw05_final
```
* создание виртуального окружения 
```
python3 -m venv venv
```
* запуск виртуального окружения 
```
. venv/bin/activate
```
* установить зависимости из файла requirements.txt 
```
pip install -r requirements.txt
```
Обновить зависимости
```
py -m pip freeze > requirements.txt
```
Создать миграции
```
- В папке с файлом manage.py выполните команду:
```
python3 manage.py runserver
```

### Зависимости:

* Python 3.7
* Django 2.2.16
```
_____________
***Над проектом работал:***
* Семёнов Юрий | GitHub: [SemenovY](https://github.com/SemenovY) | Python developer.

### *Free Software, Not for commercial use!*
### =^..^=______/
