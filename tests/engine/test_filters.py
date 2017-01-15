#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from engine.filters import *


class TestFilters(unittest.TestCase):
    # TODO: add tests for the rest of the functions

    def test_remove_protocol(self):
        urls = {
            "https://test.website.com#": "test.website.com#",
            "http://www.website.com#about": "www.website.com#about",
            "ftp://www.website.com": "www.website.com"
        }
        for url in urls:
            self.assertEqual(remove_protocol(url)[1], urls[url])

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
        urls = {
            "https://www.youtube.com/watch?v=9d8SzG4FPyM": "www.youtube.com",
            "http://www.website.com/about": "www.website.com",
            "https://google.com": "google.com"
        }
        for url in urls:
            self.assertEqual(url_to_domain(url), urls[url])

    def test_url_validator(self):
        urls = {
            "https://www.youtube.com/watch?v=9d8SzG4FPyM": True,
            "#": False,
            "https:/google.com": False
        }
        for url in urls:
            self.assertEqual(url_validator(url), urls[url])

    def test_complete_domain(self):
        urls = {
            "https://www.youtube.com/watch?v=9d8SzG4FPyM": ["https://www.youtube.com/watch?v=9d8SzG4FPyM",
                                                            "http://randomweb.com"],
            "http://github.com/gph03n1x": ["gph03n1x","https://github.com/"],
            "http://google.com/test#about": ["test#about", "https://google.com"]
        }
        for url in urls:
            self.assertEqual(complete_domain(urls[url][0], urls[url][1]), url)


suite = unittest.TestLoader().loadTestsFromTestCase(TestFilters)
unittest.TextTestRunner(verbosity=2).run(suite)
