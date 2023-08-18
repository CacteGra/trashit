#!/bin/sh
# docker-entrypoint.sh

# If this is going to be a cron container, set up the crontab.
if [ "$1" = cron ]; then
  if test -f "$FILE"; then
    echo 'Start removed manage added prod'
    rm manage.py && mv manage.production.py manage.py
    rm trashit/wsgi.py && mv trashit/wsgi.production.py trashit/wsgi.py
  fi

fi

# Launch the main container command passed as arguments.
exec "$@"

