# -*- coding: utf-8 -*-
import os
import logging
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

def http_checker(url):
    if ("http://" in url) or ("https://" in url):
        return url
    else:
        return ("http://" + url)


def myLogger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(os.getcwd() + '/' + name + '.tmp')
    logger.addHandler(handler)
    return logger


def hex_checker(email):
    if len(email) == 2:
        return str(email.decode('hex'))
    else:
        return email