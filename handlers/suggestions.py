#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import tornado.web
import logging
import tornado.escape as esc
from engine.utils import construct_regex
from engine.filters import http_checker


class SuggestionsHandler(tornado.web.RequestHandler):
    def initialize(self, search):
        self.SEARCH = search

    def post(self):
        search_string = re.split(re.compile(r'\s+') , self.get_argument('search_string').lower())
        for match in self.SEARCH.find({"search": { '$regex': construct_regex(search_string)}}):
            response = """
            <li class="list-group-item"><a onClick="a_onClick(\'%s\')">%s</a></li>
            """ % (esc.xhtml_escape(match["search"]), esc.xhtml_escape(match["search"]))
            self.write(response)
