# -*- coding: utf-8 -*-
import urllib2
import robotparser


def gather_robots_txt(domain):
    domain = url_to_domain(domain)
    robots = http_checker(self.domain) + "/robots.txt"
    try:
        self.rp = robotparser.RobotFileParser()
        self.rp.set_url(self.robots)
        self.rp.read()
    except urllib2.HTTPError:
        return None
    else:
        return self.rp


def gather_words_around_search_word(given_description, given_word, length):
    position = given_description.find(given_word)
    return given_description[position - length / 2 : position + length / 2]


def crop_fragment_identifier(url_path):
    if "#" in url_path:
        return url_path.split("#")[0]
    return url_path


def complete_domain(url_path, current_domain):
    if url_path[0] == "/":
        return "%s%s" % (current_domain, url_path)
    return url_path


def url_to_domain(url_path):
    """
    This is an experimental parser constructed in order to
    replace the get_domain which isn't accurate enough with
    the host banning
    """
    if "https://" in url_path:
        url_path = url_path.replace("https://", "")
    if "http://" in url_path:
        url_path = url_path.replace("http://", "")
    if "/" in url_path:
        url_path = url_path.split("/")[0]
    if ":" in url_path:
        url_path = url_path.split(":")[0]
    return url_path