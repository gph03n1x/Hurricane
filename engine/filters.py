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

    for word in given_words.split():

        # FILTER TRICKS AND STUFF
        if not word in given_description:
            continue
        description = given_description.split()
        count = 0
        while count < num_of_results:
            count += 1
            if word in description:
                index = description.index(word)
                results.append(index)
                description=description[description.index(word)+1:]
            else:
                break

    description = given_description.split()
    size = len(description)
    total_result = ""
    for result in results:

        total_result += " ".join(description[max(0, result-left_margin):min(size, result+right_margin)])+"\n"

    #print(description)
    #print(total_result)
    return total_result




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
