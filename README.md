TinyFastSS
==========

A simple implementation of FastSS

Design Issues
-------------

### 1. Data Persistence

Currently, FastSS uses dbm(anydbm) module to store the index data.
However, on some platforms, Python only supports 'dbm.dumb' which is
100x slower than gdbm and (seemingly) contains several bugs.

### 2. Input data

FastSS only accepts unicode strings. If bytes (or 'str' in Python 2)
are passed, it tried to decode them using the locale encoding.

### 3. Save format (a.k.a. JSON vs Pickle)

The native Pickle module is slower to encode/decode than the json module.
(Alghough, cPickle is much comparable)

Some points to consider:

* Pickle bytestream is incompatible among Python versions. We might
  avoid compatibility issues by using protocol version 2 or below.
* JSON cannot seriealize Python set objects.
