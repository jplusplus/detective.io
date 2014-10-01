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

all: install startdb run

run: clean startdb
	. $(ENV) ; python -W ignore::DeprecationWarning manage.py rqworker high default low &
	. $(ENV) ; python -W ignore::DeprecationWarning manage.py runserver --nothreading 0.0.0.0:$(PORT)

###
# Installation rules
###

$(VENV) :
	virtualenv venv --no-site-packages --distribute --prompt=Detective.io

pip_install:
	# Install pip packages
	. $(ENV) ; pip install -r requirements.txt

npm_install:
	# Install npm packages
	npm install

$(CUSTOM_D3):
	# Install a custom d3 package
	make -C `dirname $(CUSTOM_D3)`

bower_install:
	# Install bower packages
	./node_modules/.bin/bower install

neo4j_install:
	# Install neo4j locally
	./install_local_neo4j.bash $$NEO4J_VERSION

statics_install:
	. $(ENV) ; python manage.py compress --force
	rm -f $(PWD)/app/staticfiles/CACHE/img $(PWD)/app/staticfiles/CACHE/svg
	ln -sf $(PWD)/app/detective/static/detective/img/ $(PWD)/app/staticfiles/CACHE/img
	ln -sf $(PWD)/app/detective/static/detective/svg/ $(PWD)/app/staticfiles/CACHE/svg

install: $(VENV) pip_install npm_install $(CUSTOM_D3) bower_install neo4j_install statics_install

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
	./manage.py syncdb -v 0 --noinput  --traceback --pythonpath=. --settings=app.settings_tests
	# Launch test with coverage
	-python -W ignore::DeprecationWarning manage.py test $(TEST) --pythonpath=. --settings=app.settings_tests --traceback
	# Stop database in order to restore it
	make stopdb
	# Remove temporary databases
	rm -Rf lib/neo4j/data/graph.db
	# Restore backups
	mv lib/neo4j/data/graph.db.backup lib/neo4j/data/graph.db|| true
