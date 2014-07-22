==================
Installation guide
==================

Development mode
________________

**Detective.io** needs a working **python 2.7** environment with **pip**, **git**, **libmemcached** and **virtualenv**.

    .. sourcecode:: sh

        yum groupinstall "Development Tools" && yum install python python-pip python-devel git libmemcached-devel # RedHat based distribution
        apt-get install apt-get install build-essential python python-pip python-dev git libmemcached-dev         # Debian based distribution

    .. sourcecode:: sh

        pip install virtualenv

Download the source code.

    .. sourcecode:: sh

        git clone git@github.com:jplusplus/detective.io.git
        cd detective.io

Run the install script. It will create the virtualenv, install backend and frontend dependencies and setup the **Neo4j** database.

    .. sourcecode:: sh

        make install

Setup the database.

    .. sourcecode:: sh

        (. ./venv/bin/activate && ./manage.py syncdb && ./manage.py migrate all)

All we need to do now is to start the server and **Detective.io** will be available on http://localhost:8000.

    .. sourcecode:: sh

        make startdb && make run