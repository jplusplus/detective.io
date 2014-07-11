web: newrelic-admin run-program gunicorn -w 3 app.wsgi:application
worker: python manage.py rqworker high default low