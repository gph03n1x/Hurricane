# -*- coding: utf-8 -*-
import sys
import HTMLParser
from core.utils import hex_checker


def usual_filter(email):
    usuals = ["support", "help", "myaccount", "mobile", "info"]
    printabble = True
    for item in usuals:
        if item in email:
            printabble = False
    if printabble is True:
        sys.stdout.write("[info] %s\n" % (email))
        sys.stdout.flush()


def email_parser(email_string, domain="OFF", TLD="OFF"):
    # Custom email parser for cleaning up emails
    if "?" in email_string:
        email_string = email_string.split("?")[0]
    if "%" in email_string:
        # Used for removing hex values
        email_list = email_string.split("%")
        email_list = [hex_checker(item) for item in email_list]
        email_string = "".join(email_list)
    if "&" in email_string and ";" in email_string:
        #remove html entities
        try:
            htmlparser = HTMLParser.HTMLParser()
            email_string = htmlparser.unescape(email_string)
        except HTMLParser.HTMLParseError:
            pass
    if TLD == "ON":
        set_debug = 1
    elif domain == "ON":
        set_debug = 0
    if TLD == "ON" or domain == "ON":
        if "@" in email_string:
            email_domain = email_string.split("@")[1]
            return (email_domain.split(".")[set_debug])
    else:
        if "mailto:" in email_string:
            email_string = email_string.replace("mailto:", "")
        return email_string


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


def clear_host_arg(url):
    if ("http://" in url):
        url = url.replace("http://", "")
    if  ("https://" in url):
        url = url.replace("https://", "")
    if "/" in url:
        url = url.replace("/", "")
    return url


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