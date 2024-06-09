release: python manage.py migrate
release: python manage.py collectstatic --noinput
web: gunicorn projecto_billetera.wsgi