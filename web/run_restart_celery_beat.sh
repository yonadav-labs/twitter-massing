#!/usr/bin/env bash

bash -c "kill $(cat celerybeat.pid)"

sleep 1

bash -c "celery beat -A project.celery --detach -l info"
