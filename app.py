# -*- coding: utf-8 -*-

__author__ = 'John'
import re
import os.path
import tornado.ioloop
import tornado.web
import engine.crawler as crawler
from pprint import pprint

split_regex = re.compile(r'\s+')

class SearchHandler(tornado.web.RequestHandler):
    def get(self, arguments):
        self.render("main.html")
    def post(self):
        try:
            self.get_argument('search_string')
        except:
            self.render("main.html")
        else:
            search_string = re.split(split_regex , self.get_argument('search_string'))
            for part in search_string:
                #create a string like this (?=.*\bjack\b)(?=.*\bjames\b).*
                pass


class CrawlHandler(tornado.web.RequestHandler):
    def get(self, arguments):
        self.render("crawl.html")
    def post(self):
        pass


application = tornado.web.Application(
    [
    (r"/", SearchHandler),
    (r"/crawl", SearchHandler),
    (r"/crawl/(.+)", SearchHandler)
    ],
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    )

if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()