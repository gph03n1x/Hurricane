#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
if len(sys.argv) > 1:
    import tests
    sys.exit(0)

import re
import string
import os.path
import logging
import tornado.ioloop
import tornado.web
import engine.crawler as crawler
from engine.config import fetch_options
from handlers.suggestions import SuggestionsHandler
from handlers.status import StatusHandler
from handlers.search import SearchHandler

# TODO: separate tornado and crawler logs
logging.basicConfig(filename='error.log', level=logging.DEBUG)

OPTIONS = fetch_options()

crawl = crawler.Crawler(int(OPTIONS["crawler"]["threads"]), OPTIONS["crawler"]["depth"])
crawl.begin()

application = tornado.web.Application(
    [
    (r"/", SearchHandler, dict(database=crawl.get_storage())),
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
