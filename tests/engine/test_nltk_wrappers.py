#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from engine.nltk_wrappers import Description


class TestNltkWrappers(unittest.TestCase):
    # TODO: add tests for the rest of the functions
    def setUp(self):
        self.description = Description()

    def test_nltk_description(self):
        tests = {
            "one more cipher based on the vigenere encryption in a more hardened version":
                ["vigenere", 3, 3, 1, "based on the vigenere encryption in a "]
        }
        for test in tests:
            self.assertEqual(
                self.description.fetch_description(test, tests[test][0], tests[test][1], tests[test][2],
                                                   tests[test][3]), tests[test][4]
            )

    def test_detect_language(self):
        pass

suite = unittest.TestLoader().loadTestsFromTestCase(TestNltkWrappers)
unittest.TextTestRunner(verbosity=2).run(suite)
