release: python manage.py migrate --no-input
web: gunicorn -b "0.0.0.0:$PORT" -w 3 config.wsgi
