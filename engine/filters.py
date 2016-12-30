#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import itertools
import urllib.error
import urllib.robotparser
from urllib.parse import urlparse, urljoin
# Third party libraries
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
    # TODO: if there is no result create an personal function
    # https://simply-python.com/2014/03/14/saving-output-of-nltk-text-concordance/
    results = []
    count = 0
    for line in given_description[0].split('\n'):
        for word in given_words:
            if word in line:
                results.append(line)
                count += 1
        if count >= num_of_results:
            break
    print(count)
    return "\n".join(results)




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
