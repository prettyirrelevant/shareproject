release: flask db init; flask db migrate; flask db upgrade
web: gunicorn wsgi:app