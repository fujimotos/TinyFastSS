""" A simple implementation of FastSS """

import dbm
import pickle

KEY_ENCODING = 'utf8'

class FastSS:
    def __init__(self, indexdb):
        self.indexdb = indexdb

    @classmethod
    def open(cls, dbpath, flag='c'):
        return cls(dbm.open(dbpath, flag))

    def close(self):
        self.indexdb.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    @staticmethod
    def indexkeys(word):
        res, wlen = {word}, len(word)

        for i in range(wlen):
            for j in range(i, wlen):
                key = word[:i] + word[i+1:j] + word[j+1:]
                res.add(key)

        return {s.encode(KEY_ENCODING) for s in res}

    def add(self, word):
        for key in self.indexkeys(word):
            value = {word}

            if key in self.indexdb:
                value |= self.indexdb[key]

            self.indexdb[key] = pickle.dumps(value)

    def get(self, word):
        result = ([], [], [])
        candidate = set()

        for key in self.indexkeys(word):
            if key in self.indexdb:
                candidate.update(pickle.loads(self.indexdb[key]))

        for cand in candidate:
            dist = editdist(word, cand)
            if dist < 3:
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
