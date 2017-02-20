#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import json
# Third party libraries
import tornado.escape as esc
import tornado.web


class SuggestionsHandler(tornado.web.RequestHandler):
    def initialize(self, search, options):
        self.suggestions = search
        self.options = options

    def post(self):
        """
        Searches for similar saved inputs inside the database
        and returns a number of results
        :return:
        """
        #TODO: fix that.
        search = re.sub(re.compile(r'\s+'), " ", self.get_argument('search').lower())

        response = [esc.xhtml_escape(match["search"]) for match in self.suggestions.find(
            {"$text": {"$search": search}}).limit(self.options['app']['suggestions-limit'])]

        self.write(json.dumps(response))
