#!/usr/bin/env bash

set -e

# cd usholidays
alembic upgrade head
# alembic -c usholidays/alembic.ini upgrade head
# python src/usholidays/countryholidays/utils.py
# cd -

exec "$@"