#!/bin/sh
DB_NAME=$1
TEST_DB_NAME=$2
DB_ADMIN=$3
CWD=$(pwd)
USER_IN_FILE=$(grep -n "OWNER TO" "$CWD/tests/sql/test.sql" | head -n 1 | cut -d ' ' -f6 | cut -d ';' -f 1)
TEST_ENV="$CWD/.env.test"
TEST_DATABASE='test'

if [ -f $TEST_ENV ]; then
  source $TEST_ENV
fi

if ! [ -x "$(command -v psql)" ]; then
  echo 'Error: psql is not installed.' >&2
  exit 1
fi

if [ -n "$TEST_DB_NAME" ]; then
  echo "Overriding database name with ${TEST_DB_NAME}"
  TEST_DATABASE=${TEST_DB_NAME}
fi

echo "Creating ${TEST_DATABASE}"

psql $DB_NAME -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c "DROP DATABASE IF EXISTS ${TEST_DATABASE};"
psql $DB_NAME -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c "CREATE DATABASE ${TEST_DATABASE};"
psql $DB_NAME -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c "CREATE ROLE ${DATABASE_USER} LOGIN;"

psql ${TEST_DATABASE} -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c 'DROP SCHEMA IF EXISTS acct10001 CASCADE; DROP SCHEMA IF EXISTS public CASCADE;'

psql ${TEST_DATABASE} -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c 'CREATE SCHEMA public;'

cat "$CWD/tests/sql/test.sql" | sed "s/$USER_IN_FILE/${DATABASE_USER}/g" | psql ${TEST_DATABASE}  -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN


psql ${TEST_DATABASE} -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c "ALTER DATABASE ${TEST_DATABASE} OWNER TO ${DATABASE_USER};"

psql ${TEST_DATABASE} -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c "ALTER SCHEMA acct10001 OWNER TO ${DATABASE_USER};"

psql ${TEST_DATABASE} -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_ADMIN -c "ALTER SCHEMA public OWNER TO ${DATABASE_USER};"

echo "Database ${TEST_DATABASE} has been refreshed."
