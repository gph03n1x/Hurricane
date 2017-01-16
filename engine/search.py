#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
# Engine libraries
from engine.nltk_wrappers import Description

class DefaultSearch:
    def __init__(self, options, database):
        self.options = options
        self.database = database
        self.description = Description()



    def main_search(self, search):
        # TODO: complete this
        search_string = re.sub(self.options['regexes']['split'], " ", search)
        # TODO: optimize this a bit.

        start = time.time()
        matched_results = []
        for match in self.database.lists.find({"$text": {"$search": search_string}}).limit(
                self.options['app']['results-limit']):
            res = self.description.fetch_description(match['data'], search_string,
                                                     self.options['nltk']['left-margin'],
                                                     self.options['nltk']['right-margin'],
                                                     self.options['nltk']['concordance-results'])
            match['data'] = self.escape_and_bold(res, search_string)
            match['title'] = esc.xhtml_escape(match['title'])
            match['title'] = re.sub(self.options['regexes']['title-clean'], "", match['title'])
            match['url'] = "{0}{1}{2}".format(match['protocol'], "//", match["url"])

            matched_results.append(match)

        q_time = str(time.time() - start)
        if len(matched_results) > 0:
            self.database.record_search(search)

        return matched_results, q_time
        pass