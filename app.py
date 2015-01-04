# -*- coding: utf-8 -*-

__author__ = 'John'
import re
import os.path
import tornado.ioloop
import tornado.web
import engine.crawler as crawler
from engine.utils import http_checker
from pprint import pprint

split_regex = re.compile(r'\s+')

class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("main.html", results=[])
    def post(self):
        self.get_argument('search_string')
        search_string = re.split(split_regex , self.get_argument('search_string'))
        initial = r""

        for part in search_string:

            initial = r"%s(?=.*\b%s\b)" % (initial, part)
            #create a string like this (?=.*\bjack\b)(?=.*\bjames\b).*
            #pass
        initial = r"(?P<data>%s.*)\s?:(?P<url>.+)" % (initial)
        self.data_file = open("data.txt", "r")
        dt = self.data_file.read()
        matches = re.match(initial, dt)
        matched_results = [{'content': match.group('data')[:41],
                            'url': http_checker(match.group('url'))} for match in re.finditer(initial, dt)]
        pprint(matched_results)
        self.data_file.close()
        self.render("main.html", results=matched_results)
        # print(len(matches), dt)
        #print(initial, matches.group('url'))

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