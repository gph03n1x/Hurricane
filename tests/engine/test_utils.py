#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from engine.utils import *


class TestUtils(unittest.TestCase):

    def test_construct_regex(self):
        tests = {
            "how to make tests": r"((?=.*\bhow\b)(?=.*\bto\b)(?=.*\bmake\b)(?=.*\btests\b).*)"
        }
        for test in tests:
            self.assertEqual(
                construct_regex(test.split()),
                tests[test]
            )


suite = unittest.TestLoader().loadTestsFromTestCase(TestUtils)
unittest.TextTestRunner(verbosity=2).run(suite)
