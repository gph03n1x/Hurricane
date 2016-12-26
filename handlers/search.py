#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import logging
import tornado.web
import tornado.escape as esc
import engine.config
from engine.utils import construct_regex
from engine.parser import SearchParser
from engine.filters import http_checker
from engine.filters import gather_words_around_search_word as gwasw


class SearchHandler(tornado.web.RequestHandler):
    def initialize(self, database, parser, options):
        self.database = database
        self.parser = parser
        self.options = options


    def get(self):
        # Show an empty webpage ready to search
        self.render("main.html", results=[])


    def bold_(self, word):
        return "{0}{1}{2}".format("<strong>",esc.xhtml_escape(word),"</strong>")


    def escape_and_bold(self, data, search_string):
        data = esc.xhtml_escape(data)
        for word in search_string:
            data = data.replace(word, self.bold_(word))
        return data


    def post(self):
        search_string = self.parser.parse_input(self.get_argument('search_string').lower())
        search_string = re.split(re.compile(r'\s+') , search_string)

        matched_results = [
            {
                # Get the main part of the crawled webpage
                'content': self.escape_and_bold(
                    gwasw(match['data'], search_string,
                     int(self.options['nltk']['left-margin']),
                      int(self.options['nltk']['right-margin']),
                      int(self.options['nltk']['concordance-results'])),
                    search_string
                ),
                # Get the url
                'url': http_checker(match['url'])
            } for match in self.database.get_lists_collection().find({
                "data": { '$regex': construct_regex(search_string)}
            }) # Search mongodb
        ]
        
        if len(matched_results) > 0:
            self.database.record_search(self.get_argument('search_string'))

        try:
            self.get_argument('nohtml')
        except tornado.web.MissingArgumentError:
            self.render("main.html", results=matched_results)
        else:
            self.render("response.html", results=matched_results)
