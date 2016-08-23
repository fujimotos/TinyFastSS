# Makefile for TinyFastSS
#
# Mostly for developemnt.

PYTHON=/usr/bin/env python

all:

test:
	$(PYTHON) -m unittest discover -v test

.PHONY: test
