#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from engine.filters import *

class TestFilters(unittest.TestCase):
    # TODO: make more tests

    def test_gather_words_around_search_word(self):
        # TODO: fix the gather_words_around_search_word
        description = "cipher based on the vigenere encryption in a more hardened version"
        word = "vigenere"
        length = 34
        result = gather_words_around_search_word(description, word, length)
        self.assertEqual(result, "based on the vigenere encryption i")


suite = unittest.TestLoader().loadTestsFromTestCase(TestFilters)
unittest.TextTestRunner(verbosity=2).run(suite)
