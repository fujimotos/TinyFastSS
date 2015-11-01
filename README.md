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

(1) Create an index file.

```python
import fastss

with fastss.open('fastss.dat') as index:
    for word in open('dictonary.txt'):
        index.add(word.strip())
```

(2) Perform a fuzzy string search.

```python
import fastss

with fastss.open('fastss.dat') as index:
    # return a dict like: {0: ['test'], 1: ['text', 'west'], 2: ['taft']}
    print(index.query('test'))
```

Performance
-----------

A simple speed testing was done to grasp the overall performance of TinyFastSS.

The machine used in this test had Intel Core i3-4010U (1.70GHz) processor
with 4GB memory.

The dictionary used in this test was one derived from
[SCOWL v2015-08-24](http://wordlist.aspell.net/) (english-50), which
contained 98,986 English words (909 KB in disk size).

**1. Index creation performance**

* Roughly it took 3 minutes to complete the index creation.
* The size of the resulting index file was 161 MB.

```
$ time python -m fastss -c fastss.dat dictonary.txt
3m0.71s real     2m44.35s user     0m16.43s system
$ stat --format=%s fastss.dat
168214528
```

**2. Query performance**

* With randomly chosen words, it took around 5ms to perform a single search
  on average.
* The actual time varied between 1.16ms (with "nirvana") and 11.7ms (with
  "burn").

```
$ python -m timeit -s 'import fastss; index=fastss.open("fastss.dat")' 'index.query("sterner")'
100 loops, best of 3: 7.67 msec per loop
$ python -m timeit -s 'import fastss; index=fastss.open("fastss.dat")' 'index.query("spotlighted")'
100 loops, best of 3: 2.43 msec per loop
$ python -m timeit -s 'import fastss; index=fastss.open("fastss.dat")' 'index.query("burn")'
100 loops, best of 3: 11.7 msec per loop
$ python -m timeit -s 'import fastss; index=fastss.open("fastss.dat")' 'index.query("nirvana")'
1000 loops, best of 3: 1.16 msec per loop
$ python -m timeit -s 'import fastss; index=fastss.open("fastss.dat")' 'index.query("conveyor")'
100 loops, best of 3: 1.99 msec per loop
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
