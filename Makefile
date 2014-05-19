# Makefile -- Detective.io

NEO4J_VERSION = 1.9.1
ENV           = `pwd`/.env

run: clear
	. $(ENV) ; python manage.py runserver --nothreading

virtualenv:
	virtualenv venv --no-site-packages --distribute --prompt=Detective.io
	# Install pip packages
	. $(ENV) ; pip install -r requirements.txt

npm_install:
	# Install npm packages
	if [ -s npm_requirements.txt ]; then xargs -a npm_requirements.txt npm install -g; else echo '\nNo NPM dependencies found in npm_requirements.txt'; fi


install:
	make virtualenv
	# Install npm packages
	make npm_install
	# Install bower packages
	bower install
	# Install neo4j locally
	./install_local_neo4j.bash $$NEO4J_VERSION
	make startdb

clear:
	rm **/*.pyc -f

stopdb:
	./lib/neo4j/bin/neo4j stop || true

startdb:
	./lib/neo4j/bin/neo4j start || ( cat ./lib/neo4j/data/log/*.log && exit 1 )

test:
	curl -X DELETE 'http://localhost:7474/cleandb/supersecretdebugkey!'
	. $(ENV) ; python manage.py test detective --settings=app.settings_tests

# EOF
