PYTHON	= $(shell which python)

TOPDIR  = $(shell pwd)
PYDIR	= masu

OC_SOURCE	= registry.access.redhat.com/openshift3/ose
OC_VERSION	= v3.7
OC_DATA_DIR	= ${HOME}/.oc/openshift.local.data

OS := $(shell uname)
ifeq ($(OS),Darwin)
	PREFIX	=
else
	PREFIX	= sudo
endif

help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo "  clean                     clean the project directory of scratch files, bytecode, logs, etc."
	@echo "  help                      show this message"
	@echo "  lint                      run linting against the project"
	@echo "  test-db                   create database schemas and tables"
	@echo "  oc-clean                  stop openshift cluster & remove local config data"
	@echo "  oc-create-dev-db          create a Postgres DB in an initialized openshift cluster"
	@echo "  oc-create-masu            create the masu app in an initialized openshift cluster"
	@echo "  oc-create-rabbitmq        create a RabbitMQ broker in an initialized openshift cluster"
	@echo "  oc-create-tags            create image stream tags"
	@echo "  oc-dev-all                run all application services in openshift cluster"
	@echo "  oc-dev-db                 run Postgres in an openshift cluster"
	@echo "  oc-down                   stop openshift cluster and all running apps"
	@echo "  oc-forward-ports          port forward the DB to localhost"
	@echo "  oc-rm-dev                 delete Openshift objects without a cluster restart"
	@echo "  oc-test-db                create database schemas and tables"
	@echo "  oc-serve                  run Flask server locally against an Openshift DB"
	@echo "  oc-stop-forwarding-ports  stop port forwarding the DB to localhost"
	@echo "  oc-up                     initialize an openshift cluster"
	@echo "  serve                     run the Flask dev server locally"
	@echo "  unittest                  run unittests"

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

oc-up:
	oc cluster up \
		--image=$(OC_SOURCE) \
		--version=$(OC_VERSION) \
		--host-data-dir=$(OC_DATA_DIR) \
		--use-existing-config=true
	oc login -u developer --insecure-skip-tls-verify=true localhost:8443
	sleep 60

oc-down:
	oc cluster down

oc-clean: oc-down
	$(PREFIX) rm -rf $(OC_DATA_DIR)

oc-dev-db: oc-create-tags oc-create-dev-db

oc-dev-all: oc-create-tags oc-create-dev-db oc-create-masu oc-create-rabbitmq

oc-create-tags:
	oc create istag postgresql:9.6 --from-image=centos/postgresql-96-centos7
	oc create istag python-36-centos7:latest --from-image=centos/python-36-centos7

oc-create-dev-db:
	oc process openshift//postgresql-persistent \
		-p NAMESPACE=myproject \
		-p POSTGRESQL_USER=kokuadmin \
		-p POSTGRESQL_PASSWORD=admin123 \
		-p POSTGRESQL_DATABASE=koku \
		-p POSTGRESQL_VERSION=9.6 \
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

oc-rm-dev:
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

oc-forward-ports:
	-make oc-stop-forwarding-ports 2>/dev/null
	oc port-forward $$(oc get pods -o jsonpath='{.items[*].metadata.name}' -l name=koku-pgsql) 15432:5432 >/dev/null 2>&1 &
	oc port-forward rabbitmq-0 5672:5672 >/dev/null 2>&1 &

oc-stop-forwarding-ports:
	kill -HUP $$(ps -eo pid,command | grep "oc port-forward" | grep -v grep | awk '{print $$1}')

oc-serve: oc-forward-ports serve

oc-test-db: oc-forward-ports
	sleep 1
	$(TOPDIR)/tests/create_db.sh
	make oc-stop-forwarding-ports
