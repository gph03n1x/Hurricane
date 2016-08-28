#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado.web
import logging
from engine.filters import url_validator

class StatusHandler(tornado.web.RequestHandler):
    def initialize(self, crawler):
        self.crawler = crawler

    def get(self):
        urls = [self.crawler.threads[thread].current_url for thread in self.crawler.threads]
        self.render("crawl.html", results=urls)

    def post(self):
        if url_validator(self.get_argument('search_string')):
            self.crawler.add_website(self.get_argument('search_string'))
        self.redirect("/status")
