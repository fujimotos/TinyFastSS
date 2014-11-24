"""A simple implementation of FastSS

Command-line Usage:

  fastss.py -a database.dat words - Add words to the database.
  fastss.py -q database.dat words - Query the database with words.
"""

from __future__ import print_function
import dbm
import pickle
import locale
import struct
import itertools

KEY_ENCODING = 'utf8'

class FastSS:
    def __init__(self, indexdb):
        self.indexdb = indexdb
        self.dist = struct.unpack('B', indexdb['__dist__'])[0]
        self.locale_encoding = locale.getpreferredencoding()

    @classmethod
    def open(cls, dbpath, flag='c', dist=2):
        indexdb = dbm.open(dbpath, flag)

        if b'__dist__' not in indexdb:
            indexdb[b'__dist__'] = struct.pack('B', dist)

        return cls(indexdb)

    def close(self):
        self.indexdb.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    @staticmethod
    def indexkeys(word, dist):
        res = set()
        indices = tuple(range(len(word)))

        for num in range(dist+1):
            for comb in itertools.combinations(indices, num):
                key = ''.join(word[idx] for idx in indices if idx not in comb)
                res.add(key)

        return {s.encode(KEY_ENCODING) for s in res}

    def add(self, word):
        if isinstance(word, bytes):
            word = word.decode(self.locale_encoding)

        for key in self.indexkeys(word, self.dist):
            value = {word}

            if key in self.indexdb:
                value |= pickle.loads(self.indexdb[key])

            self.indexdb[key] = pickle.dumps(value)

    def get(self, word):
        result = {x: [] for x in range(self.dist+1)}
        candidate = set()

        if isinstance(word, bytes):
            word = word.decode(self.locale_encoding)

        for key in self.indexkeys(word, self.dist):
            if key in self.indexdb:
                candidate.update(pickle.loads(self.indexdb[key]))

        for cand in candidate:
            dist = editdist(word, cand)
            if dist <= self.dist:
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

if __name__ == '__main__':
    import getopt
    import sys

    ADD, QUERY = 1, 2
    action = None

    opts, args = getopt.getopt(sys.argv[1:], 'aq')
    for key, val in opts:
        if key == '-a':
            action = ADD
        elif key == "-q":
            action = QUERY

    if not action or not args:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    if action == ADD:
        with FastSS.open(args[0], 'c') as fastss:
            for word in args[1:]:
                fastss.add(word)

    elif action == QUERY:
        with FastSS.open(args[0], 'r') as fastss:
            for word in args[1:]:
                print(word, fastss.get(word), sep=': ')
