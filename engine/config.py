#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import configparser


def fetch_options():
    options = {}
    config = configparser.RawConfigParser()

    if __name__ == '__main__':
        config.read('../hurricane.cfg')
    else:
        config.read('hurricane.cfg')

    for sect in config.sections():
        options[sect] = {}
        for option in config.options(sect):
            options[sect][option] = config.get(sect, option)
            if sect == "regexes":
                options[sect][option] = re.compile(options[sect][option], re.VERBOSE | re.MULTILINE)

    return options
