#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado.web
import logging
from engine.filters import url_validator
from urllib.parse import unquote

class StatusHandler(tornado.web.RequestHandler):
    def initialize(self, crawler):
        """
        Initializes the handler by associating it with
        the crawler object .
        :param crawler:
        :return:
        """
        self.crawler = crawler

    def get(self):
        """
        Fetches the websites that are being crawled at the moment.
        :return:
        """
        urls = [self.crawler.threads[thread].current_url for thread in self.crawler.threads]
        urls_robots = []
        for thread in self.crawler.threads:
            urls_robots += [
                [unquote(domain) for domain in self.crawler.threads[thread].robots.keys()]
                ]
        self.render("crawl.html", results=urls, robots=urls_robots)

    def post(self):
        """
        Adds a website to the crawler queue
        :return:
        """
        self.crawler.add_website(self.get_argument('search'))
        self.redirect("/status")
