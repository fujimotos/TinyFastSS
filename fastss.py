"""A simple implementation of FastSS

Command-line usage:

  fastss.py -c index.dat filepath - Create a new index file.
  fastss.py -u index.dat filepath - Update the existing index.
  fastss.py -q index.dat string   - Query the index with <string>.

Create mode options:

  --maxdist <N> - Maximum edit distance for the index (default: 2)
"""

from __future__ import print_function
import locale
import struct
import itertools

#
# Python 2.X compatibility

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import anydbm as dbm
except ImportError:
    import dbm

try:
    unicode
except NameError:
    unicode = str


#
# Constants

PICKLE_PROTOCOL = 2  # The highest version with Python 2 support.
KEY_ENCODING = 'utf-8'
DIST_KEY = b'__dist__'


#
# Utils

def editdist(s1, s2):
    """Return the Levenshtein distance between two strings.

    >>> editdist('aiu', 'aie')
    1
    """

    matrix = {}

    for i in range(len(s1)+1):
        matrix[(i, 0)] = i
    for j in range(len(s2)+1):
        matrix[(0, j)] = j

    for i in range(1, len(s1)+1):
        for j in range(1, len(s2)+1):
            if s1[i-1] == s2[j-1]:
                matrix[(i, j)] = matrix[(i-1, j-1)]
            else:
                matrix[(i, j)] = min(
                    matrix[(i-1, j)],
                    matrix[(i, j-1)],
                    matrix[(i-1, j-1)]
                ) + 1

    return matrix[(i, j)]


def indexkeys(word, max_dist):
    """Return the set of index keys ("variants") of a word.

    >>> indexkeys('aiu', 1)
    {'aiu', 'iu', 'au', 'ai'}
    """

    res = set()
    wordlen = len(word)
    limit = min(max_dist, wordlen) + 1

    for dist in range(limit):
        variants = itertools.combinations(word, wordlen-dist)

        for variant in variants:
            res.add(''.join(variant))

    return res


def int2byte(i):
    """Encode a positive int (<= 256) into a 8-bit byte.

    >>> int2byte(1)
    b'\x01'
    """
    return struct.pack('B', i)


def byte2int(b):
    """Decode a 8-bit byte into an integer.

    >>> byte2int(b'\x01')
    1
    """
    return struct.unpack('B', b)[0]


#
# FastSS class

class FastSS:
    def __init__(self, index):
        self.index = index
        self.max_dist = byte2int(index[DIST_KEY])

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __contains__(self, word):
        if word in self.index:
            return word in pickle.loads(self.index[word])
        return False

    @classmethod
    def open(cls, path, flag='c', max_dist=2):
        index = dbm.open(path, flag)

        if DIST_KEY not in index:
            index[DIST_KEY] = int2byte(max_dist)

        return cls(index)

    def close(self):
        self.index.close()

    def add(self, word):
        if isinstance(word, bytes):
            word = word.decode(locale.getpreferredencoding())

        for key in indexkeys(word, self.max_dist):
            bkey = key.encode(KEY_ENCODING)
            value = {word}

            if bkey in self.index:
                value |= pickle.loads(self.index[bkey])

            self.index[bkey] = pickle.dumps(value, protocol=PICKLE_PROTOCOL)

    def query(self, word):
        result = {x: [] for x in range(self.max_dist+1)}
        candidate = set()

        if isinstance(word, bytes):
            word = word.decode(locale.getpreferredencoding())

        for key in indexkeys(word, self.max_dist):
            bkey = key.encode(KEY_ENCODING)

            if bkey in self.index:
                candidate.update(pickle.loads(self.index[bkey]))

        for cand in candidate:
            dist = editdist(word, cand)
            if dist <= self.max_dist:
                result[dist].append(cand)

        return result


# Enable a simple interface;
# >>> import fastss
# >>> fastss.open('/path/to/dbm', 'n')
builtin_open = open
open = FastSS.open

if __name__ == '__main__':
    import getopt
    import sys
    import fileinput
    import json

    CREATE, UPDATE, QUERY = 1, 2, 3
    path, action, flag = None, None, None
    max_dist = 2

    opts, args = getopt.getopt(sys.argv[1:], 'c:u:q:', 'maxdist=')
    for key, val in opts:
        if key == '-c':
            path, action, flag = val, CREATE, 'n'
        elif key == '-u':
            path, action, flag = val, UPDATE, 'c'
        elif key == "-q":
            path, action, flag = val, QUERY, 'r'
        elif key == "--maxdist":
            max_dist = int(val)

    if action is None or path is None:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    if action in (CREATE, UPDATE):
        with FastSS.open(path, flag, max_dist) as fastss:
            for line in fileinput.input(args):
                line = line.strip()
                if line:
                    fastss.add(line)

    elif action == QUERY:
        with FastSS.open(path, 'r') as fastss:
            for word in args:
                result = (word, fastss.query(word))
                print(json.dumps(result))
