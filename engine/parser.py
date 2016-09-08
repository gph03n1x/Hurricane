#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import logging
from bs4 import BeautifulSoup
from engine.config import fetch_options


class PageParser(object):
    def __init__(self, logger):
        self.logger = logger
        self.options = fetch_options()


    def parse_page(self, page):
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
        self.options = fetch_options()
        self.stop_words = []
        # TODO: find better stop words lists
        for stop_word_file in self.options['parser']['stop-word-files'].split(','):
            with open("data/stop-words/"+stop_word_file, encoding='utf8') as stop_words_file:
                self.stop_words += stop_words_file.read().split("\n")
        self.stop_words = list(set(self.stop_words))
        self.stop_words = filter(None, self.stop_words)
        pattern = "{0}{1}{2}".format("\s","\s|\s".join(self.stop_words),"\s")
        #print(pattern)
        self.pattern = re.compile(pattern)


    def parse_input(self, user_input):
        page = self.pattern.sub(" ", user_input)
        return page
