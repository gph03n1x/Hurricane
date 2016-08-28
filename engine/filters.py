#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import urllib.error
import urllib.robotparser
from urllib.parse import urlparse, urljoin


def gather_robots_txt(url):
    domain = url_to_domain(url)
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


def gather_words_around_search_word(given_description, given_word, length):
    position = given_description.find(given_word)
    return given_description[position - length // 2 : position + length // 2]


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


def complete_domain(url_path, current_url):
    try:
        if not urlparse(url_path).netloc:
            current_domain = url_to_domain(current_url)
            return "{0}{1}".format(http_checker(current_domain), url_path)
    except IndexError:
        pass
    return url_path


def http_checker(url):
    return urljoin("http://", url).replace("///", "//", 1)


def url_to_domain(url_path):
    return urlparse(url_path).netloc
