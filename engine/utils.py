#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging


def construct_regex(search_string):
    regex_string = "".join(r"(?=.*\b{0}\b)".format(part) for part in search_string)
    return r"({0}.*)".format(regex_string)


def my_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(os.getcwd() + '/' + name + '.tmp')
    logger.addHandler(handler)
    return logger
