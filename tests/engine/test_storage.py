#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from engine.storage import MongoDBRecorder

class TestStorage(unittest.TestCase):
    # TODO: add tests for the rest of the functions
    def setUp(self):
        #self.storage = MongoDBRecorder()
        pass

    def test_record_words(self):
        pass

    def test_check_url(self):
        pass

    def test_record_db(self):
        pass


suite = unittest.TestLoader().loadTestsFromTestCase(TestStorage)
unittest.TextTestRunner(verbosity=2).run(suite)
