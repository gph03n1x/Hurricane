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
        if not urlparse(url_path).netloc:
            # TODO: removes https , it shouldn't do that
            current_domain = url_to_domain(current_url)
            url_path = urljoin(http_checker(current_domain), url_path)
    except IndexError:
        pass
    return remove_backslash(url_path)


def http_checker(url):
    return urljoin("http://", url).replace("///", "//", 1)


def url_to_domain(url_path):
    return urlparse(url_path).netloc
