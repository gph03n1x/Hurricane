#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from engine.filters import crop_fragment_identifier, remove_backslash, http_checker


class TestFilters(unittest.TestCase):
    # TODO: add tests for the rest of the functions

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

    def test_http_checker(self):
        urls = {
            "//test.website.com": "http://test.website.com",
            "www.website.com/about": "http://www.website.com/about",
            "https://google.com": "https://google.com"
        }
        for url in urls:
            self.assertEqual(http_checker(url), urls[url])

    def test_url_to_domain(self):
        pass

    def test_url_validator(self):
        pass

    def test_complete_domain(self):
        pass


suite = unittest.TestLoader().loadTestsFromTestCase(TestFilters)
unittest.TextTestRunner(verbosity=2).run(suite)
