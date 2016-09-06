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
    def initialize(self, database, parser):
        self.database = database
        self.parser = parser


    def get(self):
        # Show an empty webpage ready to search
        self.render("main.html", results=[])


    def post(self):
        # TODO: Clean up search from useless spaces
        search_string = self.parser.parse_input(self.get_argument('search_string').lower())
        search_string = re.split(re.compile(r'\s+') , search_string)

        matched_results = [
            {
                # Get the main part of the crawled webpage
                # TODO: make gwasw configurable
                'content': gwasw(match['data'], search_string[0], 90),
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
            for result in matched_results:
                response = """
                <div class="panel panel-default">
                    <div class="panel-heading">
                        <a href="%s">%s</a>
                    </div>
                    <div class="panel-body">%s</div>
                </div>
                """ % (esc.xhtml_escape(result['url']),
                       esc.xhtml_escape(result['url']),
                       esc.xhtml_escape(result['content']))
                self.write(response)
