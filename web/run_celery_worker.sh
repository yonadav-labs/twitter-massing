#!/usr/bin/env bash

# wait for Redis server to start
#sleep 10

bash -c "celery worker -A project.celery -D -l info"
