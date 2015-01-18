# -*- coding: utf-8 -*-
import re
import ConfigParser

regex_patterns = {
    'split_regex': re.compile(r'\s+'),
    'escape_regex': re.compile('(\\n|\\t|\\r)'),
    'url_regex': re.compile(r'href=[\'"]?([^\'" >]+)', re.VERBOSE | re.MULTILINE),
    'body_contents': re.compile(r'<body>(.+)</body>', re.VERBOSE | re.MULTILINE)
}