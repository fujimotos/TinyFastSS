# Makefile for TinyFastSS
#
# Mostly for developemnt.

PYTHON=/usr/bin/env python

all:

test:
	$(PYTHON) -m unittest discover -v test

publish:
	$(PYTHON) setup.py sdist register upload

.PHONY: test
