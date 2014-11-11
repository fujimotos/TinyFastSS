""" A simple implementation of FastSS """


class FastSS:
    def __init__(self, indexdb=None):
        if indexdb is None:
            indexdb = {}
        self.indexdb = indexdb

    @staticmethod
    def indexkeys(word):
        res = {word}
        wlen = len(word)
        for i in range(wlen):
            for j in range(i, wlen):
                key = word[:i] + word[i+1:j] + word[j+1:]
                res.add(key)
        return res

    def add(self, word):
        for key in self.indexkeys(word):
            if key not in self.indexdb:
                self.indexdb[key] = set()
            self.indexdb[key].add(word)

    def get(self, word):
        result = [[], [], []]
        candidate = set()

        for key in self.indexkeys(word):
            if key in self.indexdb:
                candidate.update(self.indexdb[key])

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
