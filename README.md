TinyFastSS
==========

[FastSS](http://fastss.csg.uzh.ch/) is an efficient indexing data structure
for string similarity search, invented by researchers at Zurich University
in 2007.

TinyFastSS is a simple Python implementation of FastSS, written in less than
300 LoC.


Introduction
------------

Suppose you have a large English dictionary, say with 1,000,000 words,
and want to implement a fancy spell checker based on it. The first
thing you need to do is to find out a way to get the list of 'similar'
entries to an input word.

The most obvious way to do this is to go through the whole dictionary and
compare each entry against the input string. This is really simple to implement,
but your program would require (number-of-words x 1 million) computations
to perform a single spell-checking task for your documents. This easily
leads to a real performance problem.

TinyFastSS solves this problem by creating a special index file on disk.
This index data allows you to retrieve all the similar words within a distance
of *k* (you can specify this value when you create a new index file) in
an astonishingly fast manner.


Installation
------------

* Python 3.3 or later recommended (Python 2.7 is also supported)
* Download the source code and run 'setup.py':

    $ python setup.py install


How to use
----------


Implementation Notes
--------------------

### 1. Data Persistence

Currently, FastSS uses dbm(anydbm) module to store the index data.
However, on some platforms, Python only supports 'dbm.dumb' which is
100x slower than gdbm and (seemingly) contains several bugs.

### 2. Input data

FastSS only accepts unicode strings. If bytes (or 'str' in Python 2)
are passed, it tried to decode them using the locale encoding.

### 3. Save format (a.k.a. JSON vs Pickle)

Some points to consider:

* The pure-python Pickle module is really slow, while cPickle is much
  comparable in speed to the json module.
* Pickle bytestream is incompatible among Python versions, while JSON is
  language independent.
* JSON cannot serialize some Python objects (most crucial here is the set
  objects).
