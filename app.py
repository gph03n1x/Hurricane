# -*- coding: utf-8 -*-

import re
import string
import os.path
import tornado.ioloop
import tornado.web
import engine.crawler as crawler
from engine.utils import http_checker
from pprint import pprint
from pymongo import MongoClient


CLIENT = MongoClient("127.0.0.1", 27017, max_pool_size=200)
POSTS = CLIENT['test']['lists']
split_regex = re.compile(r'\s+')


class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        # Show an empty webpage ready to search
        self.render("main.html", results=[])

    def post(self):
        self.get_argument('search_string')
        # Clean up search from useless spaces
        search_string = re.split(split_regex , self.get_argument('search_string').lower())


        # Create a string like this (?=.*\bjack\b)(?=.*\bjames\b).*
        # Which is used for searching in any order for as many words
        initial = r""
        for part in search_string:
            initial = r"%s(?=.*\b%s\b)" % (initial, part)
        initial = r"(%s.*)" % (initial)

        # Fetch results from mongodb
        matched_results = [
            {
                # Get the main part of the crawled webpage
                'content': match['data'][len(match['data']) - 20 :len(match['data']) + 20],
                # Get the url
                'url': http_checker(match['urls'])
            } for match in POSTS.find({"data": { '$regex': initial}}) # Search mongodb
        ]

        self.render("main.html", results=matched_results)

class CrawlHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("crawl.html")
    def post(self):
        pass


application = tornado.web.Application(
    [
    (r"/", SearchHandler),
    (r"/crawl", SearchHandler),
    (r"/crawl/(.+)", SearchHandler)
    ],
    serve_traceback=True,
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    )

if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()