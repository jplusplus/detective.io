# Makefile -- Detective.io

NEO4J_VERSION = 1.9.1
ENV           = `pwd`/.env

run:
	. $(ENV) ; python manage.py runserver --nothreading

install:
	virtualenv venv --no-site-packages --distribute --prompt=Detective.io
	# Install pip packages
	. $(ENV) ; pip install -r requirements.txt
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

test:
	curl -X DELETE 'http://localhost:7474/cleandb/supersecretdebugkey!'
	. $(ENV) ; python manage.py test detective --settings=app.settings_tests

# EOF
