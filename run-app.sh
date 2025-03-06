#!/bin/sh
python manage.py makemigrations
python manage.py migrate
python create_user.py
python manage.py init_db
python manage.py  test app.tests.view app.tests.services
python manage.py start_scheduler
python manage.py runserver 0.0.0.0:8000
