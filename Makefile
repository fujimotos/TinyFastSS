# Makefile for TinyFastSS
#
# Mostly for development.

PYTHON=/usr/bin/env python

all:

test:
	$(PYTHON) -m unittest discover -v test

publish:
	$(PYTHON) setup.py sdist register upload

.PHONY: test
