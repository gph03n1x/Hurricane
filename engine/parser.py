#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import logging
from bs4 import BeautifulSoup
from engine.config import fetch_options


class Parser(object):
    def __init__(self, logger):
        self.logger = logger
        self.options = fetch_options()
        self.stop_words = []
        for stop_word_file in self.options['parser']['stop-word-files'].split(','):
            with open("data/stop-words/"+stop_word_file, encoding='utf8') as stop_words_file:
                self.stop_words += stop_words_file.read().split("\n")
        self.stop_words = list(set(self.stop_words))
        self.stop_words = filter(None, self.stop_words)


    def parse_page(self, page):
        # Remove unnecessary characters
        page = re.sub(self.options['regexes']['escape'] , "", page)
        page = re.sub(self.options['regexes']['split'] , " ", page)

        soup = BeautifulSoup(page, "html.parser")
        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out
        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        page = '\n'.join(chunk for chunk in chunks if chunk)

        for word in self.stop_words:
            page = page.replace(" "+word+" ", " ")
        page = re.sub(self.options['regexes']['split'] , " ", page)
        return page
