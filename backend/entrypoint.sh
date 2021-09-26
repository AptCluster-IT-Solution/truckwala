#!/bin/sh

until nc -z "$SQL_HOST" "$SQL_PORT"; do
  echo "Waiting for db..."
  sleep 1
done

python manage.py migrate
python manage.py collectstatic --no-input

exec "$@"
