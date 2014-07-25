==================
Installation guide
==================

Development mode
================

Software dependencies
---------------------

**Detective.io** needs a working **python 2.7** environment with **pip**, **git**, **libmemcached**.

.. sourcecode:: sh

    # RedHat based distribution
    yum groupinstall "Development Tools" && yum install python python-pip python-devel git libmemcached-devel
    # OR Debian based distribution
    apt-get install apt-get install build-essential python python-pip python-dev git libmemcached-dev


Python dependencies
-------------------

**Virtualenv** will help to isolate python dependencies.

.. sourcecode:: sh

    pip install virtualenv


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
    * install python dependencies with PIP
    * install node dependencies with NPM
    * install front dependencies with Bower
    * install a Neo4j database into ``./lib``
    * setup the static files



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