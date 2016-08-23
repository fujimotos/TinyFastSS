import unittest
import os
import tempfile
import itertools
import shutil

from fastss import (FastSS, editdist, indexkeys, int2byte, byte2int,
                    set2bytes, bytes2set)


class TestFastSS(unittest.TestCase):
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
        words = (
            '0', '1', '00', '01', '10', '11',
            '000', '001', '010', '011', '100', '101', '110', '111',
            '0000', '0001', '0010', '0011', '0100', '0101', '0110', '0111',
            '1000', '1001', '1010', '1011', '1100', '1101', '1110', '1111')

        with FastSS.open(dbpath, 'n') as fastss:
            for word in words:
                fastss.add(word)

            res = fastss.query('1')
            self.assertEqual(set(res[0]), {'1'})
            self.assertEqual(set(res[1]), {'0', '01', '10', '11'})
            self.assertEqual(set(res[2]), {
                '111', '001', '010', '100', '011', '101', '110', '00'
            })


class TestUtils(unittest.TestCase):

    def test_editdist(self):
        test_case = (
            {u'10'},
            {u'0', u'1', u'00', u'11', u'010', u'100', u'101', u'110'},
            {u'', u'01', u'000', u'001', u'011', u'111'})

        for dist, word_set in enumerate(test_case):
            for word in word_set:
                self.assertEqual(editdist(word, u'10'), dist)

    def test_indexkeys(self):
        keys = indexkeys('aiu', 1)
        self.assertEqual(keys, {'aiu', 'iu', 'au', 'ai'})

        keys = indexkeys('aiu', 2)
        self.assertEqual(keys, {'aiu', 'iu', 'au', 'ai', 'a', 'i', 'u'})

        keys = indexkeys('aiu', 3)
        self.assertEqual(keys, {'aiu', 'iu', 'au', 'ai', 'a', 'i', 'u', ''})

        keys = indexkeys('aiu', 4)
        self.assertEqual(keys, indexkeys('aiu', 3))

    def test_int2byte(self):
        self.assertEqual(int2byte(0), b'\x00')
        self.assertEqual(int2byte(1), b'\x01')
        self.assertEqual(int2byte(16), b'\x10')
        self.assertEqual(int2byte(255), b'\xff')

    def test_byte2int(self):
        self.assertEqual(byte2int(b'\x00'), 0)
        self.assertEqual(byte2int(b'\x01'), 1)
        self.assertEqual(byte2int(b'\x10'), 16)
        self.assertEqual(byte2int(b'\xff'), 255)

    def test_set2byte(self):
        self.assertEqual(set2bytes({}), b'')
        self.assertEqual(set2bytes({'a', 'b', 'c'}), b'a\x00b\x00c')
        self.assertEqual(
            set2bytes({u'\u3042', u'\u3043'}),
            b'\xe3\x81\x82\x00\xe3\x81\x83')

    def test_byte2set(self):
        self.assertEqual(bytes2set(b''), set())
        self.assertEqual(bytes2set(b'a\x00b\x00c'), {'a', 'b', 'c'})
        self.assertEqual(
            bytes2set(b'\xe3\x81\x82\x00\xe3\x81\x83'),
            {u'\u3042', u'\u3043'})

if __name__ == '__main__':
    unittest.main()
