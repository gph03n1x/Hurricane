#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import configparser


def validate_config():
    pass


def fetch_options(cfg_file="hurricane.cfg"):
    options = {}
    config = configparser.RawConfigParser()

    if __name__ == '__main__':
        config.read('../'+cfg_file)
    else:
        config.read(cfg_file)

    for sect in config.sections():
        options[sect] = {}
        for option in config.options(sect):
            # If it is a number we will attempt to convert to int
            try:
                value = int(config.get(sect, option))
            except ValueError:
                value = config.get(sect, option)

            options[sect][option] = value
            if sect == "regexes":
                options[sect][option] = re.compile(options[sect][option], re.VERBOSE | re.MULTILINE)

    return options
