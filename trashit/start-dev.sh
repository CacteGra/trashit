FILE=manage.production.py
if test -f "$FILE"; then
echo 'Start removed manage added prod'
rm manage.py && mv manage.dev.py manage.py
rm trashit/wsgi.py && mv trashit/wsgi.dev.py trashit/wsgi.py
fi
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py loaddata fixtures/weekdays.json --app trash.Weekday
python manage.py loaddata fixtures/thetypes.json --app trash.TheType
python manage.py loaddata fixtures/typelocales.json --app trash.TypeLocale

gunicorn trashit.wsgi:application
