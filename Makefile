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
	@echo "  clean                    to clean the project directory of any scratch files, bytecode, logs, etc."
	@echo "  help                     to show this message"
	@echo "  lint                     to run linting against the project"
	@echo "  serve                    to run the Flask dev server locally"
	@echo "  unittest                 to run unittests"
	@echo "  oc-up                    to initialize an openshift cluster"
	@echo "  oc-down                  to stop app & openshift cluster"
	@echo "  oc-clean                 to stop openshift cluster & remove local config data"
	@echo "  oc-dev-db                to run Postgres in an openshift cluster"
	@echo "  oc-dev-all               to run app and Postgres in openshift cluster"
	@echo "  oc-create-tags           to create image stream tags"
	@echo "  oc-create-dev-db         to create a Postgres DB in an initialized openshift cluster"
	@echo "  oc-create-masu           to create a the masu app in an initialized openshift cluster"
	@echo "  oc-rm-dev                to delete Openshift objects without a cluster restart"
	@echo "  oc-forward-ports         to port forward the DB to localhost"
	@echo "  oc-stop-forwarding-ports to stop port forwarding the DB to localhost"
	@echo "  oc-serve 			 	  to run Django server locally against an Openshift DB"

clean:
	git clean -fdx -e .idea/ -e *env/

lint:
	tox -elint

unittest:
	tox -e py36

serve:
	export FLASK_APP=masu; export FLASK_ENV=development; flask run

oc-up:
	oc cluster up \
		--image=$(OC_SOURCE) \
		--version=$(OC_VERSION) \
		--host-data-dir=$(OC_DATA_DIR) \
		--use-existing-config=true
	sleep 60

oc-down:
	oc cluster down

oc-clean: oc-down
	$(PREFIX) rm -rf $(OC_DATA_DIR)

oc-dev-db: oc-create-tags oc-create-db-dev

oc-dev-all: oc-create-tags oc-create-dev-db oc-create-masu

oc-create-tags:
	oc create istag postgresql:9.6 --from-image=centos/postgresql-96-centos7
	oc create istag python-36-centos7:latest --from-image=centos/python-36-centos7

oc-create-dev-db:
	oc login -u developer
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

oc-rm-dev:
	oc login -u developer
	oc delete imagestreams --all && oc delete dc --all && oc delete svc --all && oc delete bc --all && oc delete routes --all && oc delete  configmap/masu secret/masu secret/koku-pgsql pvc/koku-pgsql

oc-forward-ports:
	-make oc-stop-forwarding-ports 2>/dev/null
	oc port-forward $$(oc get pods -o jsonpath='{.items[*].metadata.name}' -l name=masu-pgsql) 15432:5432 >/dev/null 2>&1 &

oc-stop-forwarding-ports:
	kill -HUP $$(ps -eo pid,command | grep "oc port-forward" | grep -v grep | awk '{print $$1}')

oc-serve: oc-forward-ports
	export FLASK_APP=masu; export FLASK_ENV=development; flask run
	make oc-stop-forwarding-ports
