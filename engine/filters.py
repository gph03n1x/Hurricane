#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import urllib.error
import urllib.robotparser
from urllib.parse import urlparse, urljoin
import itertools
import nltk

def gather_robots_txt(domain):
    robots = http_checker(domain) + "/robots.txt"
    try:
        # logging.debug(url + "#" +  domain + "#" + robots)
        robot_parser = urllib.robotparser.RobotFileParser()
        robot_parser.set_url(robots)
        robot_parser.read()
    except urllib.error.HTTPError:
        return None
    else:
        return robot_parser


def gather_words_around_search_word(given_description, given_words,
 left_margin, right_margin, num_of_results):
    #https://simply-python.com/2014/03/14/saving-output-of-nltk-text-concordance/
    tokens = nltk.word_tokenize(given_description)
    text = nltk.Text(tokens)

    c = nltk.ConcordanceIndex(tokens, key = lambda s: s.lower())
    concordance_txt = ([[text.tokens[list(map(lambda x: x-5 if (x-left_margin)>0 else 0,[offset]))[0]:offset+right_margin]
                        for offset in c.offsets(given_word)][:num_of_results] for given_word in given_words])

    concordance_txt = itertools.chain(*concordance_txt)
    return '\n'.join([''.join([x+' ' for x in con_sub]) for con_sub in concordance_txt])


def url_validator(url):
    try:
        result = urlparse(url)
        return True if result.scheme and result.netloc else False
    except Exception as exem:
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
