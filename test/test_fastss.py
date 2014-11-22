import unittest
import os
import tempfile
import shutil
from fastss import FastSS

class TestWriteGzip(unittest.TestCase):
    DBNAME = 'test.dat'

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_indexkeys(self):
        keys = FastSS.indexkeys('test')
        self.assertEqual(keys, {b'test', b'est', b'tst', b'tet', b'tes',
                                b'st', b'et', b'es', b'tt', b'ts', b'te'})

    def test_create_database(self):
        dbpath = os.path.join(self.tmpdir, self.DBNAME)

        with FastSS.open(dbpath, 'n') as fastss:
            fastss.add('test')

        with FastSS.open(dbpath, 'r') as fastss:
            self.assertEqual(fastss.get('test'), (['test'], [], []))
            self.assertEqual(fastss.get('tes'), ([], ['test'], []))
            self.assertEqual(fastss.get('taste'), ([], [], ['test']))

if __name__ == '__main__':
    unittest.main()
