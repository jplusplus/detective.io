==================
Installation guide
==================

Development mode
================

Environnment configuration
--------------------------

We strongly recommand you to use Autoenv_ the development process and environment
variable settings. To tell **Detective.io** to run in development mode you'll need
to create a *.env_dev* file at project's root.
Then fill this file with the following variables:

.. sourcecode:: sh
    export ENV_MODE="dev"
    export DJANGO_SETTINGS_MODULE="app.settings_dev"




Software dependencies
---------------------

**Detective.io** needs a working **python 2.7** environment with **pip** and **git**.
To exececute asynchronous tasks **Detective.io** relies on **redis**.
For front-end development you will also need to have a working **NodeJS** installation with **bower**.
**Neo4j**, the graph database used by **Detective.io**, relies on **Java** to run, please consult *Java Dependencies* for more details.

Finally **Detective.io** perform images manipulation so you will need extra image
libraries to make it work properly.

.. sourcecode:: sh

    # RedHat based distribution
    yum groupinstall "Development Tools" && yum install python python-pip python-devel nodejs npm git libxml2-devel libxslt1-devel libpng12-devel libjpeg-devel
    # OR Debian based distribution
    apt-get install build-essential python python-pip nodejs npm python-dev git libxml2-dev libxslt1-dev libpng12-dev libjpeg-dev


Python dependencies
-------------------

**Virtualenv** will help to isolate python dependencies.

.. sourcecode:: sh

    pip install virtualenv

Java configuration
------------------
**Neo4J** run in a java environment and therefore if you want to run your own
Neo4j database you need to install & configure java.

First you'll need to install a JDK on your system.
.. sourcecode:: sh
    # RedHat based distribuion
    yum install java-1.7.0-openjdk
    # OR Debian based distribution
    apt-get install openjdk-7-jre

Once your JDK is installed you need to set the JAVA_HOME in your environnment.
You can do that in many ways. The simplest is to edit your shell config file
(eg: ~/.bashrc or ~/.zshrc) and add the following definition.

.. sourcecode:: sh
    JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64/


Get the sources
---------------

Download the source code.

.. sourcecode:: sh

    git clone git@github.com:jplusplus/detective.io.git
    cd detective.io

Run the install script. It will create the virtualenv, install backend and
rontend dependencies and setup the **Neo4j** database.

.. sourcecode:: sh

    make install

**This command will:**
    * install development python dependencies with PIP
    * install node dependencies with NPM
    * install front dependencies with Bower
    * install a Neo4j database into ``./lib``
    * setup the static files


Load the initial data
---------------------
At current state, you won't be able to do so much things with your


Setup the database
------------------

Detective.io uses a relational database to handle users, permissions,
investigations, etc.

.. sourcecode:: sh

    (. ./venv/bin/activate && ./manage.py syncdb && ./manage.py migrate all)


Launch
------

All we need to do now is to start the server and **Detective.io** will be
available on http://localhost:8000.

.. sourcecode:: sh

    make startdb && make run


Production mode
===============

Software Dependencies
---------------------

Additional dependencies are required to run **Detective.io** in production mode:
- PostgreSQL for "classic" relationnal tables for production purposes.
- Memcached for the cache

.. sourcecode:: sh
    # RedHat based distribution
    yum groupinstall "Production Tools" && yum install libpq-devel libmemcached-devel postgresql
    # OR Debian based distribution
    apt-get install libpq-dev libmemcached-dev postgresql


Once those additional packages are installed you can run the production installation
procedure

.. sourcecode:: sh
    make install

