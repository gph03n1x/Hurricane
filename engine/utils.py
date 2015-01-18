# -*- coding: utf-8 -*-
import os
import logging


def http_checker(url):
    if ("http://" in url) or ("https://" in url):
        return url
    else:
        if url[:2] == "//":
            return ("http:" + url)
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