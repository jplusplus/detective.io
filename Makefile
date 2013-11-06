# Makefile -- Detective.io

VIRTUALENV = venv/
NEO4J_VERSION = 1.9.1

run:
	. $(VIRTUALENV)bin/activate ; export PYTHONPATH=`pwd`/app/:$(PYTHONPATH) ; python -W ignore::DeprecationWarning manage.py runserver --nothreading

install:
	#virtualenv venv --no-site-packages --distribute --prompt=Detective.io
	# Install pip packages
	. $(VIRTUALENV)bin/activate; pip install -r requirements.txt
	# Install npm packages
	cat npm_requirements.txt | echo $1
	# Install bower packages
	bower install
	# Install neo4j locally
	./install_local_neo4j.bash $$NEO4J_VERSION
	make startdb


stopdb:
	./lib/neo4j/bin/neo4j stop || true

startdb:
	./lib/neo4j/bin/neo4j start || ( cat ./lib/neo4j/data/log/*.log && exit 1 )

# EOF