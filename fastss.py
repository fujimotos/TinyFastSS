"""A simple implementation of FastSS

Command-line usage:

  fastss.py -c index.dat wordfile - Create a new index from the word file.
  fastss.py -q index.dat string   - Query the index with <string>.

Arguments:

  wordfile - path to the dictionary file which contains a list of words
             (in a one-word-per-line manner). <sys.stdin> is used when
             the argument is omitted.
  string   - any query word.

Create mode options:

  --maxdist  <N> - maximum edit distance for the index (default: 2)
  --encoding <S> - the encoding of the dictionary file.
"""

from __future__ import print_function
import struct
import itertools

try:
    import anydbm as dbm
except ImportError:
    import dbm


#
# Constants

ENCODING = 'utf-8'
MAXDIST_KEY = b'__maxdist__'
DELIMITER = b'\x00'


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


def set2bytes(s):
    """Serialize a set of unicode strings into bytes.

    >>> set2byte({u'a', u'b', u'c')
    b'a\x00b\x00c'
    """
    lis = []
    for uword in sorted(s):
        bword = uword.encode(ENCODING)
        lis.append(bword)
    return DELIMITER.join(lis)


def bytes2set(b):
    """Deserialize bytes into a set of unicode strings.

    >>> int2byte(b'a\x00b\x00c')
    {u'a', u'b', u'c'}
    """
    if not b:
        return set()

    lis = b.split(DELIMITER)
    return set(bword.decode(ENCODING) for bword in lis)


#
# FastSS class

class FastSS:
    def __init__(self, path, flag='c', max_dist=2):
        """Open an FastSS index file on <path>.

        flag: the mode in which the index is opened. Use "r" for read-only,
              "w" for read-write, "c" for read-write (create a new index if
              not exist), "n" for read-write (always create a new index).

        max_dist: the uppser threshold of edit distance for the index. Only
                  effective when creating a new index file.
        """

        self.db = dbm.open(path, flag)

        if MAXDIST_KEY in self.db:
            self.max_dist = byte2int(self.db[MAXDIST_KEY])
        else:
            self.max_dist = max_dist
            self.db[MAXDIST_KEY] = int2byte(max_dist)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __contains__(self, word):
        bkey = word.encode(ENCODING)
        if bkey in self.db:
            return word in bytes2set(self.db[bkey])
        return False

    @classmethod
    def open(cls, path, flag='c', max_dist=2):
        """Conventional interface for opening FastSS index file"""
        return cls(path, flag, max_dist)

    def close(self):
        self.db.close()

    def add(self, word):
        for key in indexkeys(word, self.max_dist):
            bkey = key.encode(ENCODING)
            wordset = {word}

            if bkey in self.db:
                wordset |= bytes2set(self.db[bkey])

            self.db[bkey] = set2bytes(wordset)

    def query(self, word):
        res = {d: [] for d in range(self.max_dist+1)}
        cands = set()

        for key in indexkeys(word, self.max_dist):
            bkey = key.encode(ENCODING)

            if bkey in self.db:
                cands.update(bytes2set(self.db[bkey]))

        for cand in cands:
            dist = editdist(word, cand)
            if dist <= self.max_dist:
                res[dist].append(cand)

        return res


# Enable a simple interface;
# >>> import fastss
# >>> fastss.open('/path/to/dbm', 'n')
_builtin_open = open
open = FastSS.open

if __name__ == '__main__':
    import getopt
    import sys
    import fileinput
    import json

    CREATE, QUERY = 1, 2
    path, action, flag = None, None, None
    max_dist, encoding = 2, "utf-8"

    opts, args = getopt.getopt(sys.argv[1:], 'c:q:', ('maxdist=', 'encoding='))
    for key, val in opts:
        if key == '-c':
            path, action, flag = val, CREATE, 'n'
        elif key == "-q":
            path, action, flag = val, QUERY, 'r'
        elif key == "--maxdist":
            max_dist = int(val)
        elif key == "--encoding":
            encoding = val

    if action is None or path is None:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    if action == CREATE:
        with FastSS.open(path, flag, max_dist) as fastss:
            hook = fileinput.hook_encoded(encoding)
            for line in fileinput.input(args, openhook=hook):
                line = line.strip()
                if line:
                    fastss.add(line)

    elif action == QUERY:
        with FastSS.open(path, 'r') as fastss:
            for word in args:
                res = fastss.query(word)
                print(json.dumps(res))
