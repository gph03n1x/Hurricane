#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import configparser


def validate_config():
    pass


def fetch_options(cfg_file="hurricane.cfg"):
    # TODO : cfg file should be defined from the main application
    options = {}
    config = configparser.RawConfigParser()

    if __name__ == '__main__':
        config.read('../'+cfg_file)
    else:
        config.read(cfg_file)

    for sect in config.sections():
        options[sect] = {}
        for option in config.options(sect):
            options[sect][option] = config.get(sect, option)
            if sect == "regexes":
                options[sect][option] = re.compile(options[sect][option], re.VERBOSE | re.MULTILINE)

    return options
