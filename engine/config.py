# -*- coding: utf-8 -*-
import re
import os
import ConfigParser

h_options = {}
regex_patterns = {
    'split_regex': re.compile(r'\s+'),
    'escape_regex': re.compile('(\\n|\\t|\\r)'),
    'url_regex': re.compile(r'href=[\'"]?([^\'" >]+)', re.VERBOSE | re.MULTILINE),
    'body_contents': re.compile(r'<body>(.+)</body>', re.VERBOSE | re.MULTILINE)
}
config = ConfigParser.RawConfigParser()

if __name__ == '__main__':
    config.read('../hurricane.cfg')
else:
    config.read('hurricane.cfg')


for sect in config.sections():
    h_options[sect] = {}
    for option in config.options(sect):
        h_options[sect][option] = config.get(sect, option)

print h_options
"""
for f in os.listdir('stop-words'):
    print f
    rep = {"condition1": "", "condition2": "text"} # define desired replacements here

    # use these three lines to do the replacement
    rep = dict((re.escape(k), v) for k, v in rep.iteritems())
    pattern = re.compile("|".join(rep.keys()))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)"""