TinyFastSS
==========

An index data structure for approximate string search.

What is (Tiny)FastSS?
---------------------

[FastSS](http://fastss.csg.uzh.ch/) is an efficient indexing data structure
for string similarity search, invented by researchers at Zurich University
in 2007.

TinyFastSS is a simple implementation of FastSS, written in pure Python.

### Features

* Fast, exhaustive retrieval of similar words (in terms of Levenshtein
  distance) in a dictionary.
* Very large index size. The output index data might well get 100x larger
  than the original input data.

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

The native Pickle module is slower to encode/decode than the json module.
(Although, cPickle is much comparable)

Some points to consider:

* Pickle bytestream is incompatible among Python versions. We might
  avoid compatibility issues by using protocol version 2 or below.
* JSON cannot serialize Python set objects.

