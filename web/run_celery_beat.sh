#!/usr/bin/env bash

# wait for Redis server to start
#sleep 10

bash -c "celery beat -A project.celery --detach -l info"
