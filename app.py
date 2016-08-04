# -*- coding: utf-8 -*-

import re
import string
import os.path
import logging
import tornado.ioloop
import tornado.web
import tornado.escape as esc
import engine.crawler as crawler
from pprint import pprint
from pymongo import MongoClient
from engine.config import fetch_options
from engine.utils import http_checker
from engine.filters import gather_words_around_search_word as gwasw

from handlers.autocompletehandler import AutoCompleteHandler

logging.basicConfig(filename='error.log', level=logging.DEBUG)
OPTIONS = fetch_options()
crawl = crawler.Crawler(4, OPTIONS["crawler"]["depth"])
crawl.begin()
try:
    CLIENT = MongoClient("127.0.0.1", 27017)
    POSTS = CLIENT['test']['lists']
    SEARCH = CLIENT['test']['search']
    split_regex = re.compile(r'\s+')
except Exception:
    pass
else:
    print("Connection with the database was successfull")


class SearchHandler(tornado.web.RequestHandler):

    # def initialize(self, database):
        # self.DBI = database

    def get(self):
        # Show an empty webpage ready to search
        self.render("main.html", results=[])

    def record_search(self, search_string):
        record = {"search": search_string}
        if SEARCH.find(record).count() == 0:
            SEARCH.insert(record)

    def post(self):
        self.get_argument('search_string')

        # Clean up search from useless spaces
        search_string = re.split(split_regex , self.get_argument('search_string').lower())

        # Create a string like this (?=.*\bjack\b)(?=.*\bjames\b).*
        # Which is used for searching in any order for as many words

        initial = "".join(r"(?=.*\b{0}\b)".format(part) for part in search_string)
        initial = r"({0}.*)".format(initial)
        # Fetch results from mongodb
        print(initial)
        matched_results = [
            {
                # Get the main part of the crawled webpage
                'content': gwasw(match['data'], search_string[0], 90),
                # Get the url
                'url': http_checker(match['url'])
            } for match in POSTS.find({"data": { '$regex': initial}}) # Search mongodb
        ]
        if len(matched_results) > 0:
            self.record_search(self.get_argument('search_string'))
        try:
            self.get_argument('nohtml')
        except Exception:
            self.render("main.html", results=matched_results)
        else:
            for result in matched_results:
                response = """
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <a href="%s">%s</a>
                    </div>
                    <div class="panel-body">%s</div>
                </div>
                """ % (esc.xhtml_escape(result['url']),
                       esc.xhtml_escape(result['url']),
                       esc.xhtml_escape(result['content']))
                self.write(response)


class CrawlHandler(tornado.web.RequestHandler):

    def get(self):
        urls = [crawl.threads[thread].current_url for thread in crawl.threads]
        self.render("crawl.html", results=urls)

    def post(self):
        self.get_argument('search_string')
        crawl.add_website(self.get_argument('search_string'))
        self.redirect("/crawl")


application = tornado.web.Application(
    [
    (r"/", SearchHandler),
    (r"/autocomplete", AutoCompleteHandler, dict(search=SEARCH)),
    (r"/crawl", CrawlHandler)
    ],
    serve_traceback=True,
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    )

if __name__ == "__main__":

    application.listen(int(OPTIONS['app']['port']))
    print("[*] Listening :", OPTIONS['app']['port'])
    tornado.ioloop.IOLoop.instance().start()
