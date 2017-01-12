#!/usr/bin/env python
# -*- coding: utf-8 -*-
import itertools
# Third party libraries
import nltk
from nltk.corpus import stopwords


def detect_language(text):
    # TODO: This uses the stopwords not good enough against
    # an advanced user
    detected_language = "unknown"
    max_score = 0
    tokens = nltk.wordpunct_tokenize(text)
    words = [word.lower() for word in tokens]
    for language in stopwords.fileids():
        stopwords_set = set(stopwords.words(language))
        words_set = set(words)
        common_elements = words_set.intersection(stopwords_set)
        if len(common_elements) > max_score:
            detected_language = language
            max_score = len(common_elements)

    return detected_language


class Description:
    def __init__(self):
        self.treebank = nltk.tokenize.treebank.TreebankWordTokenizer()

    def fetch_description(self, given_description, given_words, left_margin, right_margin, num_of_results):
        """
        Creates a description focusing on the search words.
        """
        # https://simply-python.com/2014/03/14/saving-output-of-nltk-text-concordance/
        # Instead of using nltk.word_tokenize which
        # hangs for a long time sometimes like when using the text from
        # "url":"https://www.reddit.com/user/AutoModerator"
        # The hanging comes from nltk/tokenize/__init__
        # line 94 : return tokenizer.tokenize(text)
        # I am avoiding this prt and I am only using the TreebankWordTokenizer
        tokens = self.treebank.tokenize(given_description)

        text = nltk.Text(tokens)
        c = nltk.ConcordanceIndex(tokens, key=lambda s: s.lower())
        concordance_txt = ([[text.tokens[list(map(lambda x: x-left_margin if (x-left_margin) > 0 else left_margin-x,
                                                  [offset]))[0]:offset+right_margin+1]
                            for offset in c.offsets(given_word)][:num_of_results]
                            for given_word in given_words.split()])
        concordance_txt = itertools.chain(*concordance_txt)
        return '\n'.join([''.join([x+' ' for x in con_sub]) for con_sub in concordance_txt])
