# -*- coding: utf-8 -*-
import sys
import HTMLParser
from core.utils import hex_checker


def url_to_domain(url_path):
    """
    This is an experimental prser constructed in order to
    replace the get_domain which isn't accurate enough with
    the host banning
    """
    if "https://" in url_path:
        url_path = url_path.replace("https://", "")
    if "http://" in url_path:
        url_path = url_path.replace("http://", "")
    if "/" in url_path:
        url_path = url_path.split("/")[0]
    if ":" in url_path:
        url_path = url_path.split(":")[0]
    return url_path