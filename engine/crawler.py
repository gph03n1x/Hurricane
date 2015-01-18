# -*- coding: utf-8 -*-

import re
import string
import urllib2
import logging
import multiprocessing
import threading
from time import sleep
from datetime import datetime
from pprint import pprint
from HTMLParser import HTMLParser
from pymongo import MongoClient
from engine.filters import complete_domain, crop_fragment_identifier
import engine.config as config
import engine.storage as storage
global SCANNED_ROBOTS
SCANNED_ROBOTS = {}


url_regex = re.compile(r'href=[\'"]?([^\'" >]+)', re.VERBOSE | re.MULTILINE)
split_regex = re.compile(r'\s+')
escape_regex = re.compile('(\\n|\\t|\\r)')



class MyHTMLParser(HTMLParser):

    def reset_list(self):
        # Creates an empty list and locks it
        self.data_list = []
        self.lock = True

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            # Signal that is should start adding to the list , the following data
            self.lock = False

    def handle_data(self, data):
        if self.lock is False:
            # Adds data to the list since it found the <body> tag
            self.data_list.append(data)


class Crawler(object):

    def __init__(self, max_threads):
        self.queue = multiprocessing.Queue()
        self.threads = {}
        self.max_threads = max_threads
        # Create a data storage for the threads to use
        self.file_object = storage.pymongo_recorder(self.max_threads)

    def add_website(self, website_url):
        self.queue.put((website_url, 0)) # Add a url in the queue

    def begin(self):
        for thread in range(0, self.max_threads):
            # Spawn and start the threads
            self.threads[thread] = Worker(self.queue, self.file_object)
            self.threads[thread].start()


class Worker(threading.Thread):

    def __init__(self, queue, file_object):
        super(Worker, self).__init__()
        self.queue = queue
        self.file_object = file_object # file_object is the storage the crawler
                                       # will use .
        self.parser = MyHTMLParser()
        self.current_url = "Idle"
    def run(self):
        while True:
            try:
                if not self.queue.empty():
                    item = self.queue.get()
                    self.work(item) # crawl the item
                else:
                    self.current_url = "Idle"
                    sleep(1) # Let the thread go idle until a new item comes up
            except Exception:
                logging.exception('Worker-Exception-run()')

    def work(self, queue_item):
        # queue_item[0] is the url, queue_item[1] is the depth
        self.current_url = queue_item[0]
        self.depth = queue_item[1]
        logging.info(str(queue_item))
        if len(queue_item) > 2:
            sleep(queue_item[2])

        try:
            if self.file_object.record_url(self.current_url):
                self.parser.reset_list()

                self.req = urllib2.Request(self.current_url) # Start a url request
                self.req.add_header('User-agent', 'Hurricane/1.0')
                try:
                    self.url = urllib2.urlopen(self.req)
                except urllib2.URLError:
                    pass
                except urllib2.HTTPError:
                    if not (len(queue_item) > 2):
                        self.queue.put((self.current_url, self.depth, 1))
                else:
                    self.data = self.url.read() # Fetch the data from the webpage
                    self.encoding = self.url.headers.getparam('charset') # Fetch

                    self.urls = re.findall(url_regex, self.data) # Fetch all urls from the webpage

                    try: # If the webpage has a charset set
                        self.parser.feed(self.data.decode(self.encoding)) # Parse a decoded webpage
                    except (TypeError, UnicodeDecodeError): # If an exception is raised
                        try:
                            self.parser.feed(self.data) # Parse the webpage as it is
                        except UnicodeDecodeError:
                            self.parser.feed(self.data.decode('utf-8'))


                    self.data = "".join(self.parser.data_list) # get all the data in a long string

                    self.data = re.sub(escape_regex , "", self.data) # Remove unnecessary escape characters
                    self.data = re.sub(split_regex , " ", self.data) # Replace html spaces with only one
                    self.file_object.record_db(self.data.lower(), self.current_url) # Record the results

                    # Add the urls found in the webpage
                    for url in self.urls:
                        pprint(url)

                        if self.depth + 1 <= 2 and (not (url in self.file_object.scanned_urls)):
                            # If the url doesnt exceed 2 depth and isn't already scanned
                            pprint(url)

                            self.queue.put((complete_domain(crop_fragment_identifier(url), self.current_url) ,
                                            self.depth + 1)) # Add the url to the queue and increase the depth

        except Exception:
            logging.exception('Worker-Exception-work()')

if __name__ == '__main__':
    crawl = Crawler(2)
    crawl.add_website("http://koslib.com/")
    crawl.begin()
