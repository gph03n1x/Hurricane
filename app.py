#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import os.path
import argparse
# Third party libraries
import nltk
import tornado.ioloop
import tornado.web
# Engine libraries
import engine.crawler as crawler
from engine.config import fetch_options
from engine.parser import SearchParser
from engine.utils import construct_logger, zip_old_logs
# Handler libraries
from handlers.suggestions import SuggestionsHandler
from handlers.status import StatusHandler
from handlers.search import SearchHandler

parser = argparse.ArgumentParser()
parser.add_argument("--update",
                    help="update nltk collections",
                    action="store_true")
parser.add_argument("--tests", help="run the hurricane unittests",
                    action="store_true")
args = parser.parse_args()

if args.tests:
    import tests
    sys.exit(0)

if args.update:
    nltk.download("stopwords")
    nltk.download("punkt")

if not os.path.exists("data/logs"):
    os.mkdir("data/logs")

if not os.path.isfile("hurricane.cfg"):
    print("[-] Please rename hurricane.cfg.example to hurricane.cfg")
    print("[-] and make the appropriate changes.")
    sys.exit(0)

zip_old_logs("data/logs")

OPTIONS = fetch_options()

crawl = crawler.Crawler(int(OPTIONS["crawler"]["threads"]), OPTIONS["crawler"]["depth"])
crawl.start()
# TODO: integrate the handler logger in the handlers
handler_logger = construct_logger("data/logs/handlers")
search_parser = SearchParser(handler_logger)

application = tornado.web.Application(
    [
    (r"/", SearchHandler, dict(database=crawl.get_storage(),parser=search_parser,options=OPTIONS,logger=handler_logger)),
    (r"/suggest", SuggestionsHandler, dict(search=crawl.get_storage().get_search_collection())),
    (r"/status", StatusHandler, dict(crawler=crawl))
    ],
    serve_traceback=True,
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    )


if __name__ == "__main__":
    application.listen(int(OPTIONS['app']['port']))
    print("[*] Listening :", OPTIONS['app']['port'])
    tornado.ioloop.IOLoop.instance().start()
