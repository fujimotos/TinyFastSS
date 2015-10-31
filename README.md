TinyFastSS
==========

[FastSS](http://fastss.csg.uzh.ch/) is an efficient indexing data structure
for string similarity search, invented by researchers at Zurich University
in 2007.

TinyFastSS is a simple Python implementation of FastSS, written in less than
300 LoC.


Features
--------

* Create a FastSS index on disk.
* Perform very fast fuzzy searches using the index file.
* Python 2/3 compatible (tested with Python 2.7 / 3.4)
* No external modules required (only dependent on built-in modules)


How to install
--------------

Clone the source code and run 'setup.py':

    $ python setup.py install


Basic usage
-----------

### 1. Create an index file.

```python
import fastss

with fastss.open('fastss.dat') as index:
    for word in open('dictonary.txt'):
        index.add(word.strip())
```

### 2. Perform a fuzzy string search.

```python
import fastss

with fastss.open('fastss.dat') as index:
    # return a dict like: {0: ['test'], 1: ['text', 'west'], 2: ['taft']}
    print(index.query('test'))
```


Implementation notes
--------------------

TinyFastSS uses built-in module dbm (anydbm) to store the index data.

A "index file" is basically a (disk-based) hash table which maps a key
(read the original paper to know what a 'key' means) to a list of words.

As dbm can only store bytes, both keys and words are encoded in UTF-8,
and each word-list is serialized into a byte string delimited by null
bytes (b'\x00'). Here is an example of a (key, value) pair:

    (b'almond', b'almond\x00almonds\x00almondy')
