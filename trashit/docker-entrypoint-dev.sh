#!/bin/sh
# docker-entrypoint.sh

# If this is going to be a cron container, set up the crontab.
if [ "$1" = cron ]; then
  if test -f "$FILE"; then
    echo 'Start removed manage added prod'
    rm manage.py && mv manage.dev.py manage.py
    rm trashit/wsgi.py && mv trashit/wsgi.dev.py trashit/wsgi.py
  fi

fi
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py loaddata fixtures/weekdays.json --app trash.Weekday
# Launch the main container command passed as arguments.
exec "$@"

