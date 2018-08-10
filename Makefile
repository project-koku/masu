PYTHON	= $(shell which python)

TOPDIR  = $(shell pwd)
PYDIR	= masu

OC_SOURCE	= registry.access.redhat.com/openshift3/ose
OC_VERSION	= v3.9
OC_DATA_DIR	= ${HOME}/.oc/openshift.local.data

PGSQL_VERSION   = 9.6

OS := $(shell uname)
ifeq ($(OS),Darwin)
	PREFIX	=
else
	PREFIX	= sudo
endif

define HELP_TEXT=
Please use \`make <target>' where <target> is one of:

--- General Commands ---
  clean                     clean the project directory of scratch files, bytecode, logs, etc.
  help                      show this message
  lint                      run linting against the project

--- Commands using local services ---
  serve                     run the Flask dev server locally
  test-db                   create database schemas and tables
  unittest                  run unittests

--- Commands using an OpenShift Cluster ---
  oc-clean                  stop openshift cluster & remove local config data
  oc-create-all             run all application services in openshift cluster
  oc-create-db              create a Postgres DB in an initialized openshift cluster
  oc-create-masu            create the masu app in an initialized openshift cluster
  oc-create-rabbitmq        create a RabbitMQ broker in an initialized openshift cluster
  oc-create-tags            create image stream tags
  oc-delete-all             delete Openshift objects without a cluster restart
  oc-down                   stop openshift cluster and all running apps
  oc-forward-ports          port forward the DB to localhost
  oc-login-dev              to login to an openshift cluster as 'developer'
  oc-reinit                 remove existing app and restart app in initialized openshift cluster
  oc-serve                  run Flask server locally against an Openshift DB
  oc-stop-forwarding-ports  stop port forwarding the DB to localhost
  oc-test-db                create database schemas and tables
  oc-up                     initialize an openshift cluster
  oc-up-all                 initialize openshift cluster and run all application services
  oc-up-db                  initialize openshift cluster and run Postgres
endef
export HELP_TEXT

help:
	@echo "$$HELP_TEXT"


clean:
	git clean -fdx -e .idea/ -e *env/

lint:
	tox -elint

test-db:
	$(TOPDIR)/tests/create_db.sh

unittest:
	tox -e py36

serve:
	FLASK_APP=masu \
	FLASK_ENV=development \
	MASU_SECRET_KEY='t@@ m4nY 53Cr3tZ' \
	flask run

oc-clean: oc-down
	$(PREFIX) rm -rf $(OC_DATA_DIR)

oc-create-all: oc-create-tags oc-create-db oc-create-rabbitmq oc-create-masu

oc-create-db: oc-create-tags oc-create-db

oc-create-db:
	oc process openshift//postgresql-persistent \
		-p NAMESPACE=myproject \
		-p POSTGRESQL_USER=kokuadmin \
		-p POSTGRESQL_PASSWORD=admin123 \
		-p POSTGRESQL_DATABASE=koku \
		-p POSTGRESQL_VERSION=$(PGSQL_VERSION) \
		-p DATABASE_SERVICE_NAME=koku-pgsql \
	| oc create -f -

oc-create-masu:
	oc process -f $(TOPDIR)/openshift/masu-template.yaml \
		-p SOURCE_REPOSITORY_REF=$(shell git rev-parse --abbrev-ref HEAD) \
	| oc create -f -

oc-create-rabbitmq:
	oc process -f $(TOPDIR)/openshift/rabbitmq.yaml \
		-p SOURCE_REPOSITORY_REF=$(shell git rev-parse --abbrev-ref HEAD) \
	| oc create -f -

oc-create-tags:
	oc get istag postgresql:$(PGSQL_VERSION) || oc create istag postgresql:$(PGSQL_VERSION)} --from-image=centos/postgresql-96-centos7
	oc get istag python-36-centos7:latest || oc create istag python-36-centos7:latest --from-image=centos/python-36-centos7

oc-delete-all:
	oc delete is --all && \
	oc delete dc --all && \
	oc delete bc --all && \
	oc delete svc --all && \
	oc delete pvc --all && \
	oc delete routes --all && \
	oc delete statefulsets --all && \
	oc delete configmap/masu \
		secret/masu \
		secret/koku-pgsql \

oc-down:
	oc cluster down

oc-forward-ports:
	-make oc-stop-forwarding-ports 2>/dev/null
	oc port-forward $$(oc get pods -o jsonpath='{.items[*].metadata.name}' -l name=koku-pgsql) 15432:5432 >/dev/null 2>&1 &
	oc port-forward rabbitmq-0 5672:5672 >/dev/null 2>&1 &

oc-login-dev:
	oc login -u developer --insecure-skip-tls-verify=true localhost:8443

oc-reinit: oc-delete-all oc-create-all

oc-stop-forwarding-ports:
	kill -HUP $$(ps -eo pid,command | grep "oc port-forward" | grep -v grep | awk '{print $$1}')

oc-serve: oc-forward-ports serve

oc-test-db: oc-forward-ports
	sleep 1
	$(TOPDIR)/tests/create_db.sh
	make oc-stop-forwarding-ports

oc-up:
	oc cluster up \
		--image=$(OC_SOURCE) \
		--version=$(OC_VERSION) \
		--host-data-dir=$(OC_DATA_DIR) \
		--use-existing-config=true
	sleep 60

oc-up-all: oc-up oc-create-all

oc-up-db: oc-up oc-create-db
