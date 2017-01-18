#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Third party libraries
import tornado.web
# Engine libraries
from engine.search import DefaultSearch


class SearchHandler(tornado.web.RequestHandler):
    def initialize(self, database, parser, options, logger):
        """
        Initializes the database with parameters
        pointing to the database, parser , options dictionary
        and the logger the handler is going to use.
        :param database:
        :param parser:
        :param options:
        :param logger:
        :return:
        """
        self.database = database
        self.parser = parser
        self.options = options
        self.logger = logger
        self.search = DefaultSearch(options, database, parser)

    def get(self):
        """
        Renders the main page.
        If there is a GET argument search then
        the main page also has results on it.
        :return:
        """
        try:
            self.get_argument('search')
        except tornado.web.MissingArgumentError:
            self.render("main.html", results=[], search="", qTime="0")
        else:
            matched_results, q_time = self.search.look_up(self.get_argument('search'))
            self.render("main.html", results=matched_results, search=self.get_argument('search'), qTime=q_time)

    def post(self):
        """
        Checks for the arguments search and nohtml and renders
        the page main.html or response.html depending to the nohtml argument
        sear
        :return:
        """
        matched_results, q_time = self.search.look_up(self.get_argument('search'))

        try:
            # TODO: create an API handler
            self.get_argument('nohtml')
        except tornado.web.MissingArgumentError:
            self.render("main.html", results=matched_results, search=self.get_argument('search'), qTime=q_time)
        else:
            self.render("response.html", results=matched_results, qTime=q_time)