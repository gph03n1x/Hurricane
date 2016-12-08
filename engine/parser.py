#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import logging
from bs4 import BeautifulSoup
from engine.config import fetch_options
from nltk.corpus import stopwords


class PageParser(object):
    def __init__(self, logger):
        self.logger = logger
        self.options = fetch_options()


    def pull_urls(self, page):
        soup = BeautifulSoup(page)
        soup.prettify()
        return [anchor['href'] for anchor in soup.findAll('a', href=True)]


    def parse_page(self, page):
        # TODO: detect language
        # Remove unnecessary characters
        page = re.sub(self.options['regexes']['escape'] , "", page)
        page = re.sub(self.options['regexes']['split'] , " ", page)
        soup = BeautifulSoup(page, "html.parser")
        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        page = soup.get_text()
        page = re.sub(self.options['regexes']['split'] , " ", page)
        return page


class SearchParser(object):
    def __init__(self, logger):
        self.logger = logger
        self.stop_words = set(stopwords.words('english'))
        pattern = "{0}{1}{2}".format("\s","\s|\s".join(self.stop_words),"\s")
        self.pattern = re.compile(pattern)


    def parse_input(self, user_input):
        # TODO: detect language
        page = self.pattern.sub(" ", user_input)
        return page
