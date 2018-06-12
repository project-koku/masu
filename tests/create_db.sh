#!/bin/sh
CWD=$(pwd)
DB_USER=postgres

if ! [ -x "$(command -v psql)" ]; then
  echo 'Error: psql is not installed.' >&2
  exit 1
fi

psql postgres -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_USER -c "CREATE DATABASE ${DATABASE_NAME};"
psql postgres -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_USER -c "CREATE ROLE ${DATABASE_USER} LOGIN;"

psql ${DATABASE_NAME} -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_USER -c 'DROP SCHEMA IF EXISTS testcustomer CASCADE; DROP SCHEMA IF EXISTS public CASCADE;'

psql ${DATABASE_NAME} -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_USER -c 'CREATE SCHEMA public;'

psql ${DATABASE_NAME}  -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_USER < "$CWD/tests/sql/test.sql"


psql ${DATABASE_NAME} -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_USER -c "ALTER DATABASE ${DATABASE_NAME} OWNER TO ${DATABASE_USER};"

psql ${DATABASE_NAME} -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_USER -c "ALTER SCHEMA testcustomer OWNER TO ${DATABASE_USER};"

psql ${DATABASE_NAME} -p ${DATABASE_PORT} -h ${DATABASE_HOST} -U $DB_USER -c "ALTER SCHEMA public OWNER TO ${DATABASE_USER};"
