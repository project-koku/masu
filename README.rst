====
Masu
====

|license| |Build Status| |codecov| |Updates| |Python 3|

~~~~~
About
~~~~~

Data ingestion engine for project-koku responsible for gathering cost and usage.

Getting Started
===============

This is a Python project developed using Python 3.6. Make sure you have at least this version installed.

Development
===========

To get started developing against Masu first clone a local copy of the git repository. ::

    git clone https://github.com/project-koku/masu

Developing inside a virtual environment is recommended. A Pipfile is provided. Pipenv is recommended for combining virtual environment (virtualenv) and dependency management (pip). To install pipenv, use pip ::

    pip3 install pipenv

Then project dependencies and a virtual environment can be created using ::

    pipenv install --dev

To activate the virtual environment run ::

    pipenv shell

Running on OpenShift
--------------------
We are currently developing using OpenShift version 3.7. There are different setup requirements for Mac OS and Linux (instructions are provided for Fedora).

Run `oc cluster up` once before running the make commands to generate the referenced config file.

Openshift does offer shell/tab completion. It can be generated for either bash/zsh and is available by running `oc completion bash|zsh` The following example generates a shell script for completion and sources the file.  ::

    oc completion zsh > $HOME/.oc/oc_completion.sh
    source $HOME/.oc/oc_completion.sh

Local Development Cluster
-------------------------
The following make commands can be used to create an OpenShift cluster with the necessary components to run Masu. ::

  # Start the OpenShift cluster
  make oc-up

  # Terminate the OpenShift cluster
  make oc-down

  # Clean out local data
  make oc-clean

There are a few ways to use OpenShift while developing Masu. It is possible to spin up the entire application and its dependent services, or just the dependent services can be spun up while using the local  dev server. ::

  # Run everything through OpenShift
  make oc-dev-all

  # Run *just* a database and rabbitmq in Openshift, while running the server locally
  make oc-dev-db
  make oc-create-rabbitmq

  # Run the Flask server locally with access to the OpenShift database
  make oc-serve

  # Run the celery worker locally with access to the OpenShift rabbitmq
  celery -A masu.celery.worker --broker=amqp://localhost:5672// worker

  # To clean up your development enviornment
  make oc-rm-dev


To gain temporary access to the database within OpenShift, port forwarding is used. ::

  # Port forward to 15432
  make oc-forward-ports

  psql koku -U kokuadmin -p 15432 -h localhost

  # Stop port forwarding
  make oc-stop-forwarding-ports


Testing and Linting
-------------------

Masu uses tox to standardize the environment used when running tests. Essentially, tox manages its own virtual environment and a copy of required dependencies to run tests. To ensure a clean tox environment run ::

    tox -r

This will rebuild the tox virtual env and then run all tests.

To run unit tests specifically::

    tox -e py36

To lint the code base ::

    tox -e lint

During development it can sometimes be useful to unittest a specific module or test class. Running tox can become burdensome when rapidly iterating on tests. An `.env.test` file in the base of the masu repository can be used to quickly modify database environment variables for testing. An example .env.test file::

    DATABASE_ENGINE=postgresql
    DATABASE_NAME=test
    DATABASE_HOST=localhost
    DATABASE_PORT=15432
    DATABASE_USER=kokuadmin
    DATABASE_PASSWORD=''

An example workflow for isolated testing might look like the following ::

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
