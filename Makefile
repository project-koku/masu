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

--- Commands using Docker Compose ---
  docker-up                 run flask, worker, and rabbit services
  docker-down               shut down service containers
  docker-shell              run django and db containers with shell access to server (for pdb)
  docker-logs               connect to console logs for all services
  docker-test-all           run unittests
  
--- Commands using an OpenShift Cluster ---
  oc-clean                  stop openshift cluster & remove local config data
  oc-create-all             run all application services in openshift cluster
  oc-create-configmap       create configmaps in openshift cluster
  oc-create-db              create a Postgres DB in an openshift cluster
  oc-create-flower          create the celery monitoring app in an openshift cluster
  oc-create-masu            create the masu app in an openshift cluster
  oc-create-rabbitmq        create a RabbitMQ broker in an openshift cluster
  oc-create-secrets         create secrets in openshift cluster
  oc-create-tags            create image stream tags
  oc-create-worker          create the celery worker in an openshift cluster
  oc-delete-masu			delete Openshift masu objects without a cluster restart
  oc-delete-worker			delete Openshift worker objects without a cluster restart
  oc-delete-rabbit			delete Openshift rabbitmq objects without a cluster restart
  oc-delete-all             delete Openshift objects without a cluster restart
  oc-dev-db                 run Postgres in an openshift cluster
  oc-down                   stop openshift cluster and all running apps
  oc-forward-ports          port forward the DB to localhost
  oc-login-dev              to login to an openshift cluster as 'developer'
  oc-reinit                 remove existing app and restart app in openshift cluster
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

oc-create-all: oc-create-tags oc-create-configmap oc-create-secrets oc-create-db oc-create-rabbitmq oc-create-masu oc-create-worker oc-create-scheduler oc-create-flower

oc-create-configmap:
	oc get configmap/masu || \
	oc process -f $(TOPDIR)/openshift/configmap.yaml \
		   --param-file=$(TOPDIR)/openshift/configmap.env \
	| oc create -f -

oc-create-db:
	oc get dc/koku-pgsql || \
	oc process openshift//postgresql-persistent \
		-p NAMESPACE=myproject \
		-p POSTGRESQL_USER=kokuadmin \
		-p POSTGRESQL_PASSWORD=admin123 \
		-p POSTGRESQL_DATABASE=koku \
		-p POSTGRESQL_VERSION=$(PGSQL_VERSION) \
		-p DATABASE_SERVICE_NAME=koku-pgsql \
	| oc create -f -

oc-create-flower: oc-create-configmap oc-create-secrets
	oc get bc/masu-flower dc/masu-flower || \
	oc process -f $(TOPDIR)/openshift/flower.yaml \
		--param-file=$(TOPDIR)/openshift/flower.env \
		-p SOURCE_REPOSITORY_REF=$(shell git rev-parse --abbrev-ref HEAD) \
	| oc create -f -

oc-create-masu: oc-create-configmap oc-create-secrets
	oc get bc/masu dc/masu || \
	oc process -f $(TOPDIR)/openshift/masu.yaml \
		--param-file=$(TOPDIR)/openshift/masu.env \
		-p SOURCE_REPOSITORY_REF=$(shell git rev-parse --abbrev-ref HEAD) \
	| oc create -f -

oc-create-rabbitmq:
	oc get statefulsets/rabbitmq || \
	oc process -f $(TOPDIR)/openshift/rabbitmq.yaml \
		-p SOURCE_REPOSITORY_REF=$(shell git rev-parse --abbrev-ref HEAD) \
	| oc create -f -

oc-create-secrets:
	oc get secret/masu || \
	oc process -f $(TOPDIR)/openshift/secrets.yaml \
		   --param-file=$(TOPDIR)/openshift/secrets.env \
	| oc create -f -

oc-create-tags:
	oc get is/postgresql || \
		oc create istag postgresql:$(PGSQL_VERSION) \
			--from-image=centos/postgresql-96-centos7
	oc get is/python-36-centos7 || \
		oc create istag python-36-centos7:latest \
			--from-image=centos/python-36-centos7

oc-create-worker: oc-create-configmap oc-create-secrets
	oc get bc/masu-worker dc/masu-worker || \
	oc process -f $(TOPDIR)/openshift/worker.yaml \
		--param-file=$(TOPDIR)/openshift/worker.env \
		-p SOURCE_REPOSITORY_REF=$(shell git rev-parse --abbrev-ref HEAD) \
	| oc create -f -

oc-create-scheduler: oc-create-configmap oc-create-secrets
	oc get bc/masu-scheduler dc/masu-scheduler || \
	oc process -f $(TOPDIR)/openshift/scheduler.yaml \
		--param-file=$(TOPDIR)/openshift/scheduler.env \
		-p SOURCE_REPOSITORY_REF=$(shell git rev-parse --abbrev-ref HEAD) \
	| oc create -f -

oc-delete-scheduler:
	oc delete deploymentconfigs/masu-scheduler  \
		buildconfigs/masu-scheduler \
		imagestreams/masu-scheduler \

oc-delete-masu:
	oc delete svc/masu \
		route/masu \
		buildconfigs/masu \
		deploymentconfigs/masu \
		imagestreams/masu \

oc-delete-worker:
	oc delete deploymentconfigs/masu-worker  \
		buildconfigs/masu-worker \
		imagestreams/masu-worker \
		pvc/masu-worker-data \

oc-delete-rabbit:
	oc delete svc/rabbitmq \
		imagestreams/rabbitmq \
		rolebinding/view \
		statefulsets/rabbitmq \
		buildconfigs/rabbitmq \
		pvc/mnesia-rabbitmq-0 \
		pvc/mnesia-rabbitmq-1 \
		pvc/mnesia-rabbitmq-2 \

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

oc-dev-db: oc-create-tags oc-create-db

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

docker-up:
	docker-compose up --build -d

docker-logs:
	docker-compose logs -f

docker-shell:
	docker-compose run --service-ports server

docker-test-all:
	docker-compose -f masu-test.yml up --build

docker-down:
	docker-compose down
