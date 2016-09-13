#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado.web
import logging
from engine.filters import url_validator
from urllib.parse import unquote

class StatusHandler(tornado.web.RequestHandler):
    def initialize(self, crawler):
        self.crawler = crawler

    def get(self):
        urls = [self.crawler.threads[thread].current_url for thread in self.crawler.threads]
        urls_robots = []
        for thread in self.crawler.threads:
            urls_robots += [
                [unquote(domain) for domain in self.crawler.threads[thread].robots.keys()]
                ]
        self.render("crawl.html", results=urls, robots=urls_robots)

    def post(self):

        self.crawler.add_website(self.get_argument('search_string'))
        self.redirect("/status")
