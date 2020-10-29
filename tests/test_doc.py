import unittest

from unterwegs.nlp.doc import bow
from unterwegs.utils.db import ts, rn


class TestDoc(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_bow(self):
        bag = bow('What is the best way to add/remove stop words with spacy?')
        self.assertIn('the best way', bag)
        self.assertNotIn('What', bag)
        self.assertEqual(len(bag), 8)

    def test_coocur(self):
        rn.zadd('test1', bow('What is the best way to add/remove stop words byte with spacy?'))
        rn.zadd('test2', bow('In general, what character encoding to use is not embedded in the byte sequence itself.'))
        cnt = rn.zinterstore('test3', ['test1', 'test2'], aggregate='MIN')
        rn.expire('test1', 20)
        rn.expire('test2', 20)
        rn.expire('test3', 20)
        result = set([w.decode('utf-8') for w in rn.zrange('test3', 0, -1)])
        self.assertEqual(cnt, 1)
        self.assertIn('byte', result)


