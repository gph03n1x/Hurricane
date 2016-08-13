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
            with open("stop-words/"+stop_word_file) as stop_words_file:
                self.stop_words += stop_words_file.read().split("\n")

    def parse_page(self, page):
        page = BeautifulSoup(page).text
        # Remove unnecessary escape characters
        page = re.sub(self.options['regexes']['escape'] , "", page)
        page = re.sub(self.options['regexes']['split'] , " ", page)
        for word in self.stop_words:
            page = page.replace(" "+word+" ", " ")
        return page
