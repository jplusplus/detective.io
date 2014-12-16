# Makefile -- Detective.io
NEO4J_VERSION = 1.9.1

VENV          = venv
ENV           = ./.env
RM            = rm -fr
COVERAGE      = `which coverage`
PWD           = `pwd`

CUSTOM_D3	  = ./app/static/custom_d3/d3.js

PYC           = $(wildcard *.pyc */*.pyc app/*/*.pyc app/*/*/*.pyc app/*/*/*/*.pyc app/*/*/*/*/*.pyc)
CACHE         = $(wildcard app/staticfiles/CACHE app/media/csv-exports/)

ifndef PORT
	PORT = 8000
endif

ifndef TEST
	TEST = detective
endif

ifeq ($(ENV_MODE), prod)
	REQUIREMENTS_FILE = requirements/production
else
	REQUIREMENTS_FILE = requirements/development
endif

all: install startdb run

run: clean startdb startredis
	. $(ENV) ; python -W ignore::DeprecationWarning manage.py rqworker high default low &
	. $(ENV) ; python -W ignore::DeprecationWarning manage.py runserver --nothreading 0.0.0.0:$(PORT)

watch:
	cd app/detective/bundle; node_modules/.bin/gulp watch

###
# Installation rules
###

$(VENV) :
	virtualenv venv --no-site-packages --distribute --prompt=Detective.io

pip_install:
	. $(ENV) ; pip install -r $(REQUIREMENTS_FILE)

$(CUSTOM_D3):
	# Install a custom d3 package
	make -C `dirname $(CUSTOM_D3)`


neo4j_install:
	# Install neo4j locally
	./install_local_neo4j.bash $$NEO4J_VERSION

statics_install:
	cd app/detective/bundle; npm install; bower install; node_modules/.bin/gulp

install: $(VENV) pip_install $(CUSTOM_D3) neo4j_install statics_install

sdb:
	. $(ENV) ; ./manage.py syncdb --noinput --migrate

###
# Doc generation
###

doc:
	cd docs; make html

livedoc:
	sphinx-autobuild docs docs/_build/html

###
# Clean rules
###

clean:
	$(RM) $(PYC)
	$(RM) $(CACHE)
	. $(ENV) ; python -c "from django.core.cache import cache; cache.clear()"
	@echo "cache cleaned"

fclean: clean
	rm $(CUSTOM_D3)


startredis:
	redis-server start || true

stopredis:
	redis-server stop || true

###
# Neo4j rules
###

stopdb:
	./lib/neo4j/bin/neo4j stop || true

startdb:
	./lib/neo4j/bin/neo4j start || true

###
# Test rules
###

test:
	# Install coveralls
	pip install --use-mirrors -q coveralls
	# Stop current database to create some backups
	make stopdb
	# Do db backups
	mv lib/neo4j/data/graph.db lib/neo4j/data/graph.db.backup || true
	# Start a brand new database
	make startdb
	-python manage.py syncdb -v 0 --noinput  --traceback --pythonpath=. --settings=app.settings.testing
	# Launch test with coverage
	-python -W ignore::DeprecationWarning manage.py test $(TEST) --pythonpath=. --settings=app.settings.testing --traceback
	# Stop database in order to restore it
	make stopdb
	# Remove temporary databases
	rm -Rf lib/neo4j/data/graph.db
	# Restore backups
	mv lib/neo4j/data/graph.db.backup lib/neo4j/data/graph.db|| true
