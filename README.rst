====
Masu
====

|license| |Build Status| |codecov| |Updates| |Python 3|

~~~~~
About
~~~~~

Data ingestion engine for project-koku. Masu is responsible for gathering data about cost and resource usage.

The Masu application contains several components - a web service, message bus, and workers. Masu also uses the Koku database. Configuration and management of the database are controlled from the Koku API application.

Getting Started
===============

A basic deployment configuration is contained within the `openshift template files <https://github.com/project-koku/masu/blob/master/openshift>`__. These templates should be acceptable for most use cases.

Parameterized values for most configuration options can be set using the provided example files. Copy the example file, removing the ``.example`` suffix. Then, update the parameter values as needed.

Once the parameter files have been configured, the provided ``Makefile`` can be used to deploy the Masu components, either individually or all at once.

To deploy all Masu components at once into an existing OpenShift cluster. ::

    make oc-create-all

``make help`` will show you a complete list of the available commands.

Development
===========

Prerequisites
-------------

* Python 3.6+
* virtualenvwrapper
* pipenv

Setting up the development environment
--------------------------------------

To get started developing Masu, first clone a local copy of the git repository. ::

    git clone https://github.com/project-koku/masu

Create your virtualenv. ::

    mkvirtualenv -p python3.6 masu

    # optionally, associate the virtualenv with the masu git repo
    cd /path/to/masu.git
    setvirtualenvproject

Activate the virtual environment. ::

    workon masu

Install pipenv. ::

    pip3 install pipenv

Install the Masu dependencies, including development dependencies. ::

    pipenv install --dev

Running on OpenShift
--------------------
Our development and deployment targets center around running Masu on `OpenShift <https://www.okd.io/>`__. OpenShift has different setup requirements for Mac OS and Linux. Instructions are provided for Fedora/CentOS/RHEL.

Run ``oc cluster up`` once before running the ``make`` commands to generate the referenced config file.

Tab Completion
**************
The Openshift CLI does offer shell/tab completion. It can be generated for either bash/zsh and is available by running `oc completion bash|zsh` The following example generates a shell script for completion and sources the file.  ::

    oc completion zsh > $HOME/.oc/oc_completion.sh
    source $HOME/.oc/oc_completion.sh

Access to the Koku DB
*********************
To gain direct access to the Koku database running on OpenShift, port forwarding must be used. ::

  # Forward port 5432 on the database pod to localhost:15432
  make oc-forward-ports

  # Access the DB
  psql koku -U kokuadmin -p 15432 -h localhost

  # Stop forwarding
  make oc-stop-forwarding-ports

Local and Mixed Development
---------------------------
There are several ways to run Masu components. Depending on your development needs, it may be useful to run some or all of Masu's components locally, outside of an OpenShift environment. This section will provide some examples of possible ways to deploy Masu for development purposes. This is intended to provide ideas. It is not an exhaustive or complete list of possibilities.

1. Run everything inside OpenShift. ::
   oc-create-all

2. Run the Koku database and RabbitMQ in Openshift, but run the Masu API server locally. ::
   make oc-create-db         # deploy the DB
   make oc-create-rabbitmq   # deploy RabbitMQ
   make oc-forward-ports     # set up port forwarding for the DB & RabbitMQ
   make serve                # run the Flask API server locally

3. Run RabbitMQ in OpenShift, but run the Celery task worker locally. ::
   make oc-create-rabbitmq   # deploy RabbitMQ
   make oc-forward-ports     # set up port forwarding for the DB & RabbitMQ

   # run a local Celery worker
   celery -A masu.celery.worker --broker=amqp://localhost:5672// worker

Testing and Linting
-------------------

Masu uses ``tox`` to run unit tests. The simplest use case is to run ``tox`` from the top-most directory of the git repository with no additional arguments.

To run only the unit tests ::

    tox -e py36

To run only the linters ::

    tox -e lint

During development it can sometimes be useful to unittest a specific module or test class. To do this, create an `.env.test` file in the base of the masu repository. This can be used to modify database environment variables for development or testing.

An example .env.test file::

    MASU_SECRET_KEY='t0ta!!yr4nd0m'
    DATABASE_ENGINE=postgresql
    DATABASE_NAME=test
    DATABASE_HOST=localhost
    DATABASE_PORT=15432
    DATABASE_USER=kokuadmin
    DATABASE_PASSWORD=''

An example workflow for isolated testing ::

    ./tests/create_db.sh
    source .env.test
    python -m unittest tests.module.TestClass
    source .env


Contributing
=============

Please refer to Contributing_.


.. _Contributing: https://github.com/project-koku/masu/blob/master/CONTRIBUTING.rst

.. |license| image:: https://img.shields.io/github/license/project-koku/masu.svg
   :target: https://github.com/project-koku/masu/blob/master/LICENSE
.. |Build Status| image:: https://travis-ci.org/project-koku/masu.svg?branch=master
   :target: https://travis-ci.org/project-koku/masu
.. |codecov| image:: https://codecov.io/gh/project-koku/masu/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/project-koku/masu
.. |Updates| image:: https://pyup.io/repos/github/project-koku/masu/shield.svg?t=1524249231720
   :target: https://pyup.io/repos/github/project-koku/masu/
.. |Python 3| image:: https://pyup.io/repos/github/project-koku/masu/python-3-shield.svg?t=1524249231720
   :target: https://pyup.io/repos/github/project-koku/masu/
