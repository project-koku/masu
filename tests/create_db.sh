#!/bin/sh
TOX_DB=$1
CWD=$(pwd)
DB_ADMIN=postgres
USER_IN_FILE=$(grep -n "OWNER TO" "$CWD/tests/sql/test.sql" | head -n 1 | cut -d ' ' -f6 | cut -d ';' -f 1)
TEST_ENV="$CWD/.env.test"
NORMAL_ENV="$CWD/.env"

if [ -f $TEST_ENV ]; then
  source $TEST_ENV
fi

if ! [ -x "$(command -v psql)" ]; then
  echo 'Error: psql is not installed.' >&2
  exit 1
fi

if [ -n "$TOX_DB" ]; then
  echo "Overriding database name with ${TOX_DB}"
  DATABASE_NAME=${TOX_DB}
fi

echo "Creating ${DATABASE_NAME}"

psql postgres -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c "DROP DATABASE IF EXISTS ${DATABASE_NAME};"
psql postgres -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c "CREATE DATABASE ${DATABASE_NAME};"
psql postgres -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c "CREATE ROLE ${DATABASE_USER} LOGIN;"

psql ${DATABASE_NAME} -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c 'DROP SCHEMA IF EXISTS testcustomer CASCADE; DROP SCHEMA IF EXISTS public CASCADE;'

psql ${DATABASE_NAME} -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c 'CREATE SCHEMA public;'

cat "$CWD/tests/sql/test.sql" | sed "s/$USER_IN_FILE/${DATABASE_USER}/g" | psql ${DATABASE_NAME}  -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN


psql ${DATABASE_NAME} -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c "ALTER DATABASE ${DATABASE_NAME} OWNER TO ${DATABASE_USER};"

psql ${DATABASE_NAME} -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c "ALTER SCHEMA testcustomer OWNER TO ${DATABASE_USER};"

psql ${DATABASE_NAME} -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c "ALTER SCHEMA public OWNER TO ${DATABASE_USER};"

echo "Database ${DATABASE_NAME} has been refreshed."
