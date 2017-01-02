#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
# Third party libraries
import tornado.escape as esc
import tornado.web
# Engine libraries
from engine.filters import http_checker


class SuggestionsHandler(tornado.web.RequestHandler):
    def initialize(self, search, options):
        self.SEARCH = search
        self.options = options


    def post(self):
        search_string = re.sub(re.compile(r'\s+'), " ", self.get_argument('search_string').lower())
        for match in self.SEARCH.find( { "$text": { "$search": search_string } }).limit(self.options['app']['results-limit']):
            response = """
            <li class="list-group-item"><a onClick="a_onClick(\'%s\')">%s</a></li>
            """ % (esc.xhtml_escape(match["search"]), esc.xhtml_escape(match["search"]))
            self.write(response)
