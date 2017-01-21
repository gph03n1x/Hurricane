#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import time
# Third party libraries
import tornado.escape as esc
# Engine libraries
from engine.nltk_wrappers import Description

class DefaultSearch:
    def __init__(self, options, database, parser):
        self.options = options
        self.database = database
        self.parser = parser
        self.description = Description()



    def look_up(self, search):
        """
        Searches the database for data associated with the input
        :param search_input:
        :return:
         List: [{"data": "...", "url": "...", },]
         Float: q_time
        """
        search = self.parser.parse_input(search.lower())
        search = re.sub(self.options['regexes']['split'], " ", search)


        start = time.time()
        matched_results = [{
            'data': escape_and_bold(
                self.description.fetch_description(match['data'], search, self.options['nltk']['left-margin'],
                                                   self.options['nltk']['right-margin'],
                                                   self.options['nltk']['concordance-results']),
                search),
            'title': re.sub(self.options['regexes']['title-clean'], "", esc.xhtml_escape(match['title'])),
            'url': "{0}{1}{2}".format(match['protocol'], "//", match["url"]),
            'protocol': match['protocol']
                           }

            for match in self.database.lists.find({"$text": {"$search": search}}).limit(
                self.options['app']['results-limit'])
                           ]

        q_time = str(time.time() - start)
        if len(matched_results) > 0:
            self.database.record_search(search)

        return matched_results, q_time


def __bold(word):
    """
    Takes a word escapes it and
    adds strong tags around it
    :param word:
    :return: String
    """
    return "{0}{1}{2}".format("<strong>", esc.xhtml_escape(word), "</strong>")


def escape_and_bold(data, search):
    """
    Takes the description and bolds every word that
    is part of the search.
    :param data:
    :param search:
    :return: String
    """
    data = esc.xhtml_escape(data)
    for word in search.split():
        data = data.replace(word, __bold(word))
    return data