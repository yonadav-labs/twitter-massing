#!/bin/sh
# wait-for-postgres
sleep 5
bash "wait-postgres.sh"
bash -c "python manage.py db init && python manage.py db migrate && python manage.py db upgrade && python manage.py create_admin && /usr/local/bin/gunicorn -w 2 -b :8000 project:app"
