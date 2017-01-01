#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import itertools
from urllib.parse import urlparse, urljoin
# Third party libraries
import nltk


def nltk_description(given_description, given_words, left_margin,
 right_margin, num_of_results):
    """
    Creates a description focusing on the search words.
    """
    # https://simply-python.com/2014/03/14/saving-output-of-nltk-text-concordance/
    tokens = nltk.word_tokenize(given_description)
    text = nltk.Text(tokens)

    c = nltk.ConcordanceIndex(tokens, key = lambda s: s.lower())
    concordance_txt = ([[text.tokens[list(map(lambda x: x-left_margin if (x-left_margin)>0 else left_margin-x,[offset]))[0]:offset+right_margin+1]
                        for offset in c.offsets(given_word)][:num_of_results] for given_word in given_words.split()])

    concordance_txt = itertools.chain(*concordance_txt)
    return '\n'.join([''.join([x+' ' for x in con_sub]) for con_sub in concordance_txt])


def url_validator(url):
    try:
        result = urlparse(url)
        return True if result.scheme and result.netloc else False
    except Exception as exem:
        # TODO: log properly
        print(exem)
        return False


def crop_fragment_identifier(url_path):
    if "#" in url_path:
        return url_path.split("#")[0]
    return url_path


def remove_backslash(url_path):
    if url_path[-1] == "/":
        return url_path[:-1]
    return url_path


def complete_domain(url_path, current_url):
    try:
        if not urlparse(url_path).netloc:
            current_domain = url_to_domain(current_url)
            url_path = urljoin(http_checker(current_domain), url_path)
    except IndexError:
        pass
    return remove_backslash(url_path)


def http_checker(url):
    return urljoin("http://", url).replace("///", "//", 1)


def url_to_domain(url_path):
    return urlparse(url_path).netloc
