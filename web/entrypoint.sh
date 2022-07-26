./manage.py migrate;
./manage.py compilemessages;
./manage.py collectstatic --noinput;
gunicorn --bind=0.0.0.0:"$DJANGO_PORT" --timeout=90 --workers=2 --preload shahnameh.wsgi:application;
