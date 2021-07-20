#!/bin/bash

SUPERVISORD_CONFIGPATH=/opt/config/supervisord.conf
GUNICORN_CONFIGPATH=/opt/config/gunicorn_config.py

if [ ! -f EXECUTED ]; then
    if [ -z "${WORKERS}" ]; then
        WORKERS=4
    fi

    echo "
[supervisord]
nodaemon = true

[program:app]
command = gunicorn -c ${GUNICORN_CONFIGPATH} run:app --chdir /opt/${BASE_NAME}/
startsecs = 5
startretries = 50
autostart = true
    " > ${SUPERVISORD_CONFIGPATH}

    echo "
worker_connections = 1000
timeout = 120
max_requests = 2000
graceful_timeout = 120
loglevel = 'info'
preload_app = True
reload = True
debug = True
bind = '0.0.0.0:5000'
errorlog = '/opt/log/gunicorn_error.log'
accesslog = '/opt/log/gunicorn_access.log'
workers = ${WORKERS}
worker_class = 'egg:meinheld#gunicorn_worker'
x_forwarded_for_header = 'X-FORWARDED-FOR'
    " > ${GUNICORN_CONFIGPATH}

    touch EXECUTED
fi

if [ ${MODE} = 'develop' ]; then
    while true; do
        python3 ${BASE_NAME}/run.py
        sleep 5;
    done
else
    supervisord -c ${SUPERVISORD_CONFIGPATH}
fi
