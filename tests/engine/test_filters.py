#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from engine.filters import *


class TestFilters(unittest.TestCase):
    # TODO: add tests for the rest of the functions
    def test_nltk_description(self):
        tests = {
            "one more cipher based on the vigenere encryption in a more hardened version":["vigenere", 3, 3, 1, "based on the vigenere encryption in a "]
        }
        for test in tests:
            self.assertEqual(
                nltk_description(test,
                 tests[test][0], tests[test][1], tests[test][2],
                  tests[test][3]
                ),
                 tests[test][4]
            )

    def test_crop_fragment_identifier(self):
        urls = {
            "https://test.website.com#": "https://test.website.com",
            "https://www.website.com#about": "https://www.website.com",
            "https://www.website.com": "https://www.website.com"
        }
        for url in urls:
            self.assertEqual(crop_fragment_identifier(url), urls[url])

    def test_remove_backslash(self):
        urls = {
            "https://test.website.com/": "https://test.website.com",
            "https://www.website.com/about": "https://www.website.com/about"
        }
        for url in urls:
            self.assertEqual(remove_backslash(url), urls[url])


suite = unittest.TestLoader().loadTestsFromTestCase(TestFilters)
unittest.TextTestRunner(verbosity=2).run(suite)
