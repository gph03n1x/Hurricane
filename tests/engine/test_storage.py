#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from engine.filters import crop_fragment_identifier, remove_backslash, http_checker


class TestStorage(unittest.TestCase):
    # TODO: add tests for the rest of the functions
    def setUp(self):
        pass

    def test_crop_fragment_identifier(self):
        urls = {
            "https://test.website.com#": "https://test.website.com",
            "https://www.website.com#about": "https://www.website.com",
            "https://www.website.com": "https://www.website.com"
        }
        for url in urls:
            self.assertEqual(crop_fragment_identifier(url), urls[url])



suite = unittest.TestLoader().loadTestsFromTestCase(TestStorage)
unittest.TextTestRunner(verbosity=2).run(suite)
