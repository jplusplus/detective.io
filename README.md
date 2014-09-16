# Detective.io [![Build Status](https://travis-ci.org/jplusplus/detective.io.svg?branch=master)](https://travis-ci.org/jplusplus/detective.io)

[Download](https://github.com/jplusplus/detective.io/archive/master.zip) •
[Fork](https://github.com/jplusplus/detective.io) •
[License](https://github.com/jplusplus/detective.io/blob/master/LICENSE) •
[Test coverage](https://coveralls.io/r/jplusplus/detective.io) •
[Documentation](http://docs.detective.io/en/latest/) •
*Version 1.7.5 Seepferd*

## Installation

See also the [full installation guide](http://docs.detective.io/en/latest/installation.html).

**1. Prerequisite**
```bash
sudo apt-get install build-essential git-core python python-pip python-dev libmemcached-dev
sudo pip install virtualenv
```

**2.  Download the project**
```bash
git clone git@github.com:jplusplus/detective.io.git
cd detective.io
```

**3. Install**
```bash
make install
```

## Run in development
```bash
make run
```

Then visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Technical stack

This small application uses the following tools and opensource projects:

* [Django Framework](https://www.djangoproject.com/) - Backend Web framework
* [Neo4django](https://github.com/scholrly/neo4django) - Object Graph Mapper for Neo4j
* [Tastypie](https://github.com/toastdriven/django-tastypie) - RestAPI for Django
* [AngularJS](https://angularjs.org/) - Javascript Framework
* [UI Router](https://github.com/angular-ui/ui-router) - Application states manager
* [Underscore](http://underscorejs.org/) - Utility library
* [Bootstrap](http://getbootstrap.com/) - HTML and CSS framework
* [Less](http://lesscss.org/) - CSS pre-processor
* [CoffeeScript](http://coffeescript.org/)
