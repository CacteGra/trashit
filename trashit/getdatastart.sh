FILE=manage.production.py
if test -f "$FILE"; then
sleep 30
echo 'Start removed manage added prod'
rm manage.py && mv manage.production.py manage.py
rm trashit/wsgi.py && mv trashit/wsgi.production.py trashit/wsgi.py
fi
python manage.py migrate --noinput
python manage.py makemigrations --noinput
python manage.py loaddata fixtures/weekdays.json --app trash.Weekday
python manage.py crontab add
sleep 10
python manage.py crontab show
python manage.py get-data
# Launch the main container command passed as arguments.
exec "$@"
