#!/bin/sh
set -e

python manage.py makemigrations --noinput

python manage.py migrate --noinput

python manage.py collectstatic --noinput --skip-checks

# 啟動服務
exec "$@"
