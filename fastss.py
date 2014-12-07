"""A simple implementation of FastSS

Command-line Usage:

  fastss.py -c database.dat filepath - Create new database with input stream.
  fastss.py -u database.dat filepath - Update database using input stream.
  fastss.py -q database.dat string   - Query database with string.

Create Options:

  --maxdist <N> - Maximum edit distance for the database (default: 2)
"""

from __future__ import print_function
import locale
import struct
import itertools

# For Python 2.X compatibility
try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import anydbm as dbm
except ImportError:
    import dbm

# Constant
KEY_ENCODING = 'utf8'
PICKLE_PROTOCOL = 2

class FastSS:
    def __init__(self, indexdb):
        self.indexdb = indexdb
        self.max_dist = struct.unpack('B', indexdb['__dist__'])[0]

    @classmethod
    def open(cls, dbpath, flag='c', max_dist=2):
        indexdb = dbm.open(dbpath, flag)

        if b'__dist__' not in indexdb:
            indexdb[b'__dist__'] = struct.pack('B', max_dist)

        return cls(indexdb)

    def close(self):
        self.indexdb.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __contains__(self, word):
        if word in self.indexdb:
            return word in pickle.loads(self.indexdb[word])
        return false

    @staticmethod
    def indexkeys(word, max_dist):
        res = set()
        indices = tuple(range(len(word)))

        for num in range(max_dist+1):
            for comb in itertools.combinations(indices, num):
                key = ''.join(word[idx] for idx in indices if idx not in comb)
                res.add(key)

        return {s.encode(KEY_ENCODING) for s in res}

    def add(self, word):
        if isinstance(word, bytes):
            word = word.decode(locale.getpreferredencoding())

        for key in self.indexkeys(word, self.max_dist):
            value = {word}

            if key in self.indexdb:
                value |= pickle.loads(self.indexdb[key])

            self.indexdb[key] = pickle.dumps(value, protocol=PICKLE_PROTOCOL)

    def remove(self, word):
        if isinstance(word, bytes):
            word = word.decode(locale.getpreferredencoding())

        for key in self.indexkeys(word, self.max_dist):
            if key not in self.indexdb:
                raise KeyError(word)

            value = pickle.loads(self.indexdb[key])

            if word not in value:
                raise KeyError(word)

            self.indexdb[key] = pickle.dumps(value - {word})

    def query(self, word):
        result = {x: [] for x in range(self.max_dist+1)}
        candidate = set()

        if isinstance(word, bytes):
            word = word.decode(locale.getpreferredencoding())

        for key in self.indexkeys(word, self.max_dist):
            if key in self.indexdb:
                candidate.update(pickle.loads(self.indexdb[key]))

        for cand in candidate:
            dist = editdist(word, cand)
            if dist <= self.max_dist:
                result[dist].append(cand)

        return result


def editdist(s, t):
    """Calculate Levenshtein distance between two strings"""

    matrix = {}
    for i in range(len(s)+1):
        matrix[(i, 0)] = i
    for j in range(len(t)+1):
        matrix[(0, j)] = j

    for j in range(1, len(t)+1):
        for i in range(1, len(s)+1):
            if s[i-1] == t[j-1]:
                matrix[(i, j)] = matrix[(i-1, j-1)]
            else:
                matrix[(i, j)] = min(matrix[(i-1, j)], matrix[(i, j-1)],
                                     matrix[(i-1, j-1)]) + 1

    return matrix[(i, j)]

# Enable a siimpler interface;
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
    dbpath, action, flag = None, None, None
    max_dist = 2

    opts, args = getopt.getopt(sys.argv[1:], 'c:u:q:', 'maxdist=')
    for key, val in opts:
        if key == '-c':
            dbpath, action, flag = val, CREATE, 'n'
        elif key == '-u':
            dbpath, action, flag = val, UPDATE, 'c'
        elif key == "-q":
            dbpath, action, flag = val, QUERY, 'r'
        elif key == "--maxdist":
            max_dist = int(val)

    if action is None or dbpath is None:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    if action in (CREATE, UPDATE):
        with FastSS.open(dbpath, flag, max_dist) as fastss:
            for line in fileinput.input(args):
                line = line.strip()
                if line:
                    fastss.add(line)

    elif action == QUERY:
        with FastSS.open(dbpath, 'r') as fastss:
            for word in args:
                result = (word, fastss.query(word))
                print(json.dumps(result))
