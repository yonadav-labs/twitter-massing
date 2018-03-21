#! /bin/sh

bash -c "/usr/local/bin/gunicorn -w 2 -b :8000 project:app --daemon"
bash ./run_celery_worker.sh
bash ./run_celery_beat.sh
