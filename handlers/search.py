#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
# Third party libraries
import tornado.web
import tornado.escape as esc
# Engine libraries
import engine.config
from engine.parser import SearchParser
from engine.filters import http_checker
from engine.filters import gather_words_around_search_word as gwasw


class SearchHandler(tornado.web.RequestHandler):
    def initialize(self, database, parser, options, logger):
        self.database = database
        self.parser = parser
        self.options = options
        self.logger = logger


    def get(self):
        # Show an empty webpage ready to search
        self.render("main.html", results=[])


    def bold_(self, word):
        return "{0}{1}{2}".format("<strong>",esc.xhtml_escape(word),"</strong>")


    def escape_and_bold(self, data, search_string):
        data = esc.xhtml_escape(data)
        for word in search_string.split():
            data = data.replace(word, self.bold_(word))
        return data


    def post(self):

        search_string = self.parser.parse_input(self.get_argument('search_string').lower())
        search_string = re.sub(re.compile(r'\s+'), " ", search_string)
        matched_results = []
        for match in self.database.lists.find({ "$text": { "$search": search_string } }):
            res = gwasw(match['data'], search_string, int(self.options['nltk']['left-margin']), int(self.options['nltk']['right-margin']),
            int(self.options['nltk']['concordance-results']))
            match['data'] = self.escape_and_bold(res, search_string)
            matched_results.append(match)

        if len(matched_results) > 0:
            self.database.record_search(self.get_argument('search_string'))

        try:
            self.get_argument('nohtml')
        except tornado.web.MissingArgumentError:
            self.render("main.html", results=matched_results)
        else:
            self.render("response.html", results=matched_results)
