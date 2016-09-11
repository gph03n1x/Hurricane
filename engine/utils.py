#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging


def construct_regex(search_string):
    regex_string = "".join(r"(?=.*\b{0}\b)".format(part) for part in search_string)
    return r"({0}.*)".format(regex_string)


def construct_logger(name):
    # TODO: make a logger that will zip old logs
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(os.getcwd() + '/' + name + '.txt')
    logger.addHandler(handler)
    return logger
