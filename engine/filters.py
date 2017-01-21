#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib.parse import urlparse, urljoin


def remove_protocol(url):
    return url.split("//", 1)


def url_validator(url):
    try:
        result = urlparse(url)
        return True if result.scheme and result.netloc else False
    except Exception as exem:
        # TODO: log properly
        print(exem)
        return False


def crop_fragment_identifier(url_path):
    if "#" in url_path:
        return url_path.split("#")[0]
    return url_path


def remove_backslash(url_path):
    if url_path[-1] == "/":
        return url_path[:-1]
    return url_path


def complete_domain(url_path, current_url):
    try:
        parsed_url = urlparse(url_path)
        if not parsed_url.netloc:
            protocol = remove_protocol(current_url)[0]
            current_domain = url_to_domain(current_url)
            url_path = urljoin(http_checker(current_domain, scheme=protocol), url_path)
    except IndexError:
        pass
    return remove_backslash(url_path)


def http_checker(url, scheme="http:"):
    scheme = "{0}{1}".format(scheme, "//")
    return urljoin(scheme, url).replace("///", "//", 1)


def url_to_domain(url_path):
    return urlparse(url_path).netloc
