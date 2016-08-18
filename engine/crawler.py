#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import string
import logging
import threading
import urllib.request
import urllib.error
import multiprocessing
from time import sleep
from pymongo import MongoClient
from engine.filters import complete_domain, crop_fragment_identifier, url_validator
from engine.config import fetch_options
from engine.parser import Parser
from engine.storage import PymongoRecorder


class Crawler(object):
    def __init__(self, max_threads, max_depth):
        self.queue = multiprocessing.Queue()
        self.threads = {}
        self.max_threads = max_threads
        self.max_depth = max_depth
        self.storage = PymongoRecorder()
        self.parser = Parser()

    def get_storage(self):
        return self.storage

    def add_website(self, website_url):
        self.queue.put((website_url, 0)) # Add a url in the queue

    def begin(self):
        for thread in range(0, self.max_threads):
            # Spawn and start the threads
            self.threads[thread] = Worker(self.max_depth, self.queue, self.storage, self.parser)
            self.threads[thread].start()


class Worker(threading.Thread):
    def __init__(self, max_depth, queue, storage, parser):
        super(Worker, self).__init__()
        self.queue = queue
        self.max_depth = int(max_depth)
        self.storage = storage # storage is the storage the crawler
                                       # will use
        self.parser = parser
        with open("stop-words/stop-words-english1.txt") as stop_words_file:
            self.stop_words = stop_words_file.read().split("\n")

        self.current_url = "Idle"

        self.options = fetch_options()

    def should_ignore(self, url):
        # Find a better method for staff like
        # static/greyindex.css?v=893e07cd07891c47f58b0a256b82ac7b
        for extension in self.options['crawler']['ignore-extensions'].split(','):
            if url.endswith("."+extension):
                return True
        return False


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
                logging.exception('Worker::run')

    def work(self, queue_item):
        # queue_item[0] is the url, queue_item[1] is the depth
        self.current_url = queue_item[0]
        self.depth = queue_item[1]
        logging.info(str(queue_item))
        if len(queue_item) > 2:
            sleep(queue_item[2])

        try:
            if self.storage.record_url(self.current_url):
                try:
                    self.req = urllib.request.Request(self.current_url,
                     headers={'User-Agent': 'Hurricane/1.1'})
                    self.url = urllib.request.urlopen(self.req)
                except urllib.error.URLError as url_error:
                    logging.exception("Worker::work::try")
                except urllib.error.HTTPError:
                    if not (len(queue_item) > 2):
                        self.queue.put((self.current_url, self.depth, 1))
                else:
                    self.data = self.url.read()
                    self.encoding = self.url.headers.get_content_charset()
                    if self.encoding is None:
                        # it is bytes probably ,ex: images
                        return # nothing more to do here.

                    self.data = self.data.decode(self.encoding) # Fetch the data from the webpage

                    self.urls = re.findall(self.options['regexes']['url'], self.data) # Fetch all urls from the webpage
                    #self.urls = filter(None, self.urls)
                    try: # If the webpage has a charset set
                        self.data = self.parser.parse_page(self.data.lower()) # Parse a decoded webpage
                    except (TypeError, UnicodeDecodeError): # If an exception is raised
                        self.data = self.parser.parse_page(self.data.decode('utf-8').lower()) # parsing with utf-8 decoded

                    self.storage.record_db(self.data, self.current_url) # Record the results

                    # Add the urls found in the webpage
                    for url in self.urls:

                        fixed_url = complete_domain(crop_fragment_identifier(url), self.current_url)
                        logging.debug(str((fixed_url,url_validator(fixed_url),self.should_ignore(fixed_url))))
                        if self.should_ignore(fixed_url) or len(fixed_url) < 1:
                            continue



                        if not url_validator(fixed_url):
                            continue

                        if self.depth + 1 <= self.max_depth and self.storage.record_url(fixed_url):
                            # If the url doesnt exceed 2 depth and isn't already scanned
                            self.queue.put((fixed_url ,
                                            self.depth + 1)) # Add the url to the queue and increase the depth

        except Exception:
            logging.exception('Worker::work')
