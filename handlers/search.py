#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import logging
import tornado.web
import tornado.escape as esc
import engine.config
from engine.utils import construct_regex
from engine.filters import http_checker
from engine.filters import gather_words_around_search_word as gwasw


class SearchHandler(tornado.web.RequestHandler):
    def initialize(self, database):
        self.database = database

    def get(self):
        # Show an empty webpage ready to search
        self.render("main.html", results=[])

    def record_search(self, search_string): # move it to storage.py
        record = {"search": search_string}
        if self.database.get_search_collection().find(record).count() == 0:
            self.database.get_search_collection().insert(record)

    def post(self):
        # Clean up search from useless spaces
        search_string = re.split(re.compile(r'\s+') , self.get_argument('search_string').lower())

        matched_results = [
            {
                # Get the main part of the crawled webpage
                'content': gwasw(match['data'], search_string[0], 90),
                # Get the url
                'url': http_checker(match['url'])
            } for match in self.database.get_lists_collection().find({
                "data": { '$regex': construct_regex(search_string)}
            }) # Search mongodb
        ]
        if len(matched_results) > 0:
            self.record_search(self.get_argument('search_string'))
        try:
            self.get_argument('nohtml')
        except Exception:
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
