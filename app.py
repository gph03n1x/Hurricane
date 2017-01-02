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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--update",
                        help="update nltk collections",
                        action="store_true")
    parser.add_argument("--tests", help="run the hurricane unittests",
                        action="store_true")
    parser.add_argument("-c", "--config", help="Pass a configure through cmd")
    parser.add_argument("-s", "--spider",
                        help="Pass a website you want to crawl only.")
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
    if args.config is not None:
        OPTIONS = fetch_options(args.config)
    else:
        OPTIONS = fetch_options()

    crawl = crawler.Crawler(OPTIONS)

    if args.spider is not None:
        print("[*] Starting the spider ...")
        crawl.add_website(args.spider)
        # TODO: check if all of the workers have gone idle
        # And when they are all idle , kill them
        # Sounds dark tbh
        crawl.run()
        sys.exit(0)
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

    application.listen(int(OPTIONS['app']['port']))
    print("[*] Listening :", OPTIONS['app']['port'])
    tornado.ioloop.IOLoop.instance().start()
