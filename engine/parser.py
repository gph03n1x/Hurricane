#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup
from engine.config import fetch_options


class Parser(object):
    def __init__(self):
        self.options = fetch_options()
        self.stop_words = []
        for stop_word_file in self.options['parser']['stop-word-files'].split(','):
            with open("stop-words/"+stop_word_file, encoding='utf8') as stop_words_file:
                self.stop_words += stop_words_file.read().split("\n")
        self.stop_words = list(set(self.stop_words))
        self.stop_words = filter(None, self.stop_words)

    def parse_page(self, page):
        # Remove unnecessary characters
        page = re.sub(self.options['regexes']['escape'] , "", page)
        page = re.sub(self.options['regexes']['split'] , " ", page)
        page = BeautifulSoup(page).text
        for word in self.stop_words:
            page = page.replace(" "+word+" ", " ")
        page = re.sub(self.options['regexes']['split'] , " ", page)
        return page
