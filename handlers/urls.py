#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Third party libraries
import tornado.web
# Engine libraries
from engine.search import DefaultSearch


class UrlsHandler(tornado.web.RequestHandler):
    def initialize(self, database, options, logger):
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
        self.options = options
        self.logger = logger

    def get(self):
        """
        Redirects to the search handler
        :return:
        """
        self.redirect("/")

    def post(self):
        """
        Checks for the arguments search and nohtml and renders
        the page main.html or response.html depending to the nohtml argument
        sear
        :return:
        """
        pass