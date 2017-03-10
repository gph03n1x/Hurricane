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
        search = re.sub(re.compile(r'\s+'), " ", self.get_argument('search').lower())
        query = {"query": {"match": {"search": search}}}
        results = self.suggestions.search(index="user_search", doc_type="user_search", body=query)

        response = [esc.xhtml_escape(match['_source']["search"])
                    for match in results['hits']['hits']]

        self.write(json.dumps(response))
