# Makefile -- Detective.io

D3 = ./d3.js

GIT_URL = https://github.com/mbostock/d3.git
D3_FOLDER = ./node_modules/d3/

SMASH = ./node_modules/.bin/smash
RM = rm -rf

_LIBRARY_FILES = src/start.js \
				src/end.js
LIBRARY_FILES = $(addprefix $(D3_FOLDER), $(_LIBRARY_FILES))

all: $(D3) clean

$(D3): install_deps
	$(SMASH) $(LIBRARY_FILES) > $@

install_deps:
	npm install

clean:
	$(RM) ./node_modules