#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
# Third party libraries
import tornado.web
import tornado.escape as esc
# Engine libraries
import engine.config
from engine.parser import SearchParser
from engine.filters import http_checker
from engine.nltk_wrappers import Description


class SearchHandler(tornado.web.RequestHandler):
    def initialize(self, database, parser, options, logger):
        self.database = database
        self.parser = parser
        self.options = options
        self.logger = logger
        self.description = Description()


    def get(self):
        # Show an empty webpage ready to search
        try:
            self.get_argument('search')
        except tornado.web.MissingArgumentError:
            self.render("main.html", results=[], search="", qTime="0")
        else:
            matched_results, qTime = self.search(self.get_argument('search'))
            self.render("main.html", results=matched_results, search=self.get_argument('search'), qTime=qTime)


    def bold_(self, word):
        return "{0}{1}{2}".format("<strong>",esc.xhtml_escape(word),"</strong>")


    def escape_and_bold(self, data, search_string):
        data = esc.xhtml_escape(data)
        for word in search_string.split():
            data = data.replace(word, self.bold_(word))
        return data


    def post(self):
        matched_results, qTime = self.search(self.get_argument('search_string'))

        try:
            self.get_argument('nohtml')
        except tornado.web.MissingArgumentError:
            self.render("main.html", results=matched_results, search=self.get_argument('search_string'), qTime=qTime)
        else:
            self.render("response.html", results=matched_results, qTime=qTime)


    def search(self, search_input):
        search_string = self.parser.parse_input(search_input.lower())
        search_string = re.sub(self.options['regexes']['split'], " ", search_string)
        # TODO: optimize this a bit.

        start = time.time()
        matched_results = []
        for match in self.database.lists.find({ "$text": { "$search": search_string } }).limit(self.options['app']['results-limit']):
            res = self.description.fetch_description(match['data'], search_string, self.options['nltk']['left-margin'], self.options['nltk']['right-margin'],
            self.options['nltk']['concordance-results'])
            match['data'] = self.escape_and_bold(res, search_string)
            match['title'] = esc.xhtml_escape(match['title'])
            match['title'] = re.sub(self.options['regexes']['title-clean'], "", match['title'])
            match['url'] = "{0}{1}{2}".format(match['protocol'], "//", match["url"])


            matched_results.append(match)

        qTime = str(time.time() - start)
        if len(matched_results) > 0:
            self.database.record_search(search_input)

        return matched_results, qTime
