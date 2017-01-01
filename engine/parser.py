#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import logging
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from engine.config import fetch_options
from engine.utils import detect_language


class PageParser(object):
    def __init__(self, logger):
        self.logger = logger
        self.options = fetch_options()


    def pull_urls(self, page):
        soup = BeautifulSoup(page, "html.parser")
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

        title = ""
        if hasattr(soup.title, 'title'):
            title = soup.title.text

        page = soup.get_text()
        page = re.sub(self.options['regexes']['split'] , " ", page)
        self.logger.debug(detect_language(page))
        return page, title


class SearchParser(object):
    def __init__(self, logger):
        self.logger = logger
        self.stop_words = set(stopwords.words('english'))
        pattern = "{0}{1}{2}".format("\s","\s|\s".join(self.stop_words),"\s")
        self.pattern = re.compile(pattern)


    def parse_input(self, user_input):
        # TODO: detect language
        self.logger.debug(detect_language(user_input))
        page = self.pattern.sub(" ", user_input)

        return page
