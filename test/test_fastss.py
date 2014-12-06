import unittest
import os
import tempfile
import itertools
import shutil
from fastss import FastSS

class TestManipulateDB(unittest.TestCase):
    DBNAME = 'test.dat'

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_create_database(self):
        dbpath = os.path.join(self.tmpdir, self.DBNAME)
        max_dist = 2

        with FastSS.open(dbpath, 'n', max_dist=max_dist) as fastss:
            pass

        with FastSS.open(dbpath, 'r') as fastss:
            self.assertEqual(fastss.max_dist, max_dist)

    def test_add_words(self):
        dbpath = os.path.join(self.tmpdir, self.DBNAME)
        word_set = ('0', '1', '00', '01', '10', '11', '000', '001', '010', '011',
                    '100', '101', '110', '111', '0000', '0001', '0010', '0011',
                    '0100', '0101', '0110', '0111', '1000', '1001', '1010', '1011',
                    '1100', '1101', '1110', '1111')

        with FastSS.open(dbpath, 'n') as fastss:
            for word in word_set:
                fastss.add(word)

            res = fastss.query('1')
            self.assertEqual(set(res[0]), {'1'})
            self.assertEqual(set(res[1]), {'0', '01', '10', '11'})
            self.assertEqual(set(res[2]), {'111', '001', '010', '100', '011', '101', '110', '00'})

    def test_remove_words(self):
        dbpath = os.path.join(self.tmpdir, self.DBNAME)
        word_set = ('0', '1', '00', '01', '10', '11', '000', '001', '010', '011',
                    '100', '101', '110', '111', '0000', '0001', '0010', '0011',
                    '0100', '0101', '0110', '0111', '1000', '1001', '1010', '1011',
                    '1100', '1101', '1110', '1111')

        with FastSS.open(dbpath, 'n') as fastss:
            for word in word_set:
                fastss.add(word)

            fastss.remove('1')
            fastss.remove('01')
            fastss.remove('001')

            res = fastss.query('1')
            self.assertEqual(set(res[0]), set())
            self.assertEqual(set(res[1]), {'0', '10', '11'})
            self.assertEqual(set(res[2]), {'111', '010', '100', '011', '101', '110', '00'})

    def test_remove_nonexist(self):
        dbpath = os.path.join(self.tmpdir, self.DBNAME)

        with FastSS.open(dbpath, 'n') as fastss:
            fastss.add('potato')

            with self.assertRaises(KeyError):
                fastss.remove('tomato')

            with self.assertRaises(KeyError):
                fastss.remove('otato')

class TestCreateIndex(unittest.TestCase):
    def test_indexkeys(self):
        keys = FastSS.indexkeys('test', 1)
        self.assertEqual(keys, {b'test', b'est', b'tst', b'tet', b'tes'})

        keys = FastSS.indexkeys('test', 2)
        self.assertEqual(keys, {b'test', b'est', b'tst', b'tet', b'tes',
                                b'st', b'et', b'es', b'tt', b'ts', b'te'})

        keys = FastSS.indexkeys('test', 3)
        self.assertEqual(keys, {b'test', b'est', b'tst', b'tet', b'tes',
                                b'st', b'et', b'es', b'tt', b'ts', b'te',
                                b't', b'e', b's', b't'})

        keys = FastSS.indexkeys('test', 4)
        self.assertEqual(keys, {b'test', b'est', b'tst', b'tet', b'tes',
                                b'st', b'et', b'es', b'tt', b'ts', b'te',
                                b't', b'e', b's', b't', b''})

if __name__ == '__main__':
    unittest.main()
