#!/bin/bash

set -euo pipefail

# Commands:
#
#   wsgi            -- run gunicorn with Django WSGI
#   celeryd         -- run celery worker
#   celerybeat      -- run celerybeat daemon
#
# Environment Variables:
#
#   APP_DIR         -- path to application directory
#                      default: "/usr/src/app"
#   CELERY_QUEUES   -- argument for Celery queues
#                      default: "default,query,import" (all)
#   CELERY_WORKERS  -- celery concurrency/process count
#                      default: "8"
#
#   NO_WAIT         -- skip waiting for servers
#                      default: "0"
#   WAIT_HOSTS      -- hosts to wait for with `wait`
#                      default: "postgres:5432, redis:6379"
#
#   HTTP_HOST       -- host to listen on
#                      default: 0.0.0.0
#   HTTP_PORT       -- port
#                      default: 8080
#   LOG_LEVEL       -- logging verbosity
#                      default: info
#   GUNICORN_TIMEOUT -- timeout for gunicorn workers in seconds
#                       default: 600

APP_DIR=${APP_DIR-/usr/src/app}
CELERY_QUEUES=${CELERY_QUEUES-default,query,import}
CELERY_WORKERS=${CELERY_WORKERS-8}
NO_WAIT=${NO_WAIT-0}
export WAIT_HOSTS=${WAIT_HOSTS-postgres:5432, redis:6379}
export PYTHONUNBUFFERED=${PYTHONUNBUFFERED-1}
HTTP_HOST=${HTTP_HOST-0.0.0.0}
HTTP_PORT=${HTTP_PORT-8080}
LOG_LEVEL=${LOG_LEVEL-info}
GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT-600}

if [[ "$NO_WAIT" -ne 1 ]]; then
  /usr/local/bin/wait

  if [ -z "$DATABASE_URL" ]; then
    PGPASSWORD=$POSTGRES_PASSWORD
    PSQL="pg_isready -h $POSTGRES_HOST -p 5432 -U $POSTGRES_USERNAME"
  else
    PSQL="pg_isready -d $DATABASE_URL"
  fi
fi

if [[ "$1" == wsgi ]]; then
  cd $APP_DIR

  >&2 echo "VARFISH MIGRATIONS BEGIN"
  python manage.py migrate
  >&2 echo "VARFISH MIGRATIONS END"

  exec gunicorn \
    --access-logfile - \
    --log-level "$LOG_LEVEL" \
    --bind "$HTTP_HOST:$HTTP_PORT" \
    --timeout "$GUNICORN_TIMEOUT" \
    config.wsgi
elif [[ "$1" == celeryd ]]; then
  cd $APP_DIR

  exec celery worker \
    --app config.celery_app \
    -Q "${CELERY_QUEUES}" \
    --concurrency "${CELERY_WORKERS}" \
    --loglevel info
elif [[ "$1" == celerybeat ]]; then
  cd $APP_DIR
  rm -f celerybeat.pid

  exec celery beat \
    --max-interval 30 \
    --app config.celery_app \
    --loglevel info
else
  cd $APP_DIR
  exec "$@"
fi

exit $?
