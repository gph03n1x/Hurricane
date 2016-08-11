#!/usr/bin/env python
import tornado.web
import logging
import tornado.escape as esc

class AutoCompleteHandler(tornado.web.RequestHandler):
    def initialize(self, search):
        self.SEARCH = search

    def post(self):
        initial = "(.*%s.*)" % (self.get_argument('search_string'))
        for match in self.SEARCH.find({"search": { '$regex': initial}}):
            response = """
            <li class="list-group-item"><a onClick="a_onClick(\'%s\')">%s</a></li>
            """ % (esc.xhtml_escape(match["search"]), esc.xhtml_escape(match["search"]))
            self.write(response)
