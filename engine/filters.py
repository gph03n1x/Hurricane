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

def tag_gather(page_data, args):
    target = '<meta name="keywords" content="'
    try:
        website = page_data.split(target)
        end_ = website[1].find('"')
        full_data = website[1][:end_]
        if (" " in full_data) and ("," in full_data):
            full_data = full_data.replace(" ", "")
        elif " " in full_data:
            full_data = full_data.replace(" ", ",")
        if args.google:
            return "%s,%s" % (full_data, args.google)
        else:
            return "%s,%s" % (full_data, args.host)
    except:
        if args.google:
            return "%s" % (args.google)
        else:
            return "%s" % (args.host)