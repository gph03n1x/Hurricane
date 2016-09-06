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
from engine.filters import *
from engine.config import fetch_options
from engine.parser import PageParser
from engine.storage import MongoDBRecorder
from engine.utils import construct_logger


class Crawler(object):
    def __init__(self, max_threads, max_depth):
        self.queue = multiprocessing.Queue()
        self.threads = {}
        self.max_threads = max_threads
        self.max_depth = max_depth
        self.logger = construct_logger("data/logs/crawler")
        self.storage = MongoDBRecorder(self.logger)
        self.parser = PageParser(self.logger)


    def get_storage(self):
        return self.storage


    def get_logger(self):
        return self.logger


    def add_website(self, website_url):
        self.queue.put((website_url, 0)) # Add a url in the queue


    def begin(self):
        for thread in range(0, self.max_threads):
            # Spawn and start the threads
            self.threads[thread] = Worker(self.max_depth, self.logger,
             self.queue, self.storage, self.parser)
            self.threads[thread].start()


class Worker(threading.Thread):
    def __init__(self, max_depth, logger, queue, storage, parser):
        super(Worker, self).__init__()
        self.max_depth = int(max_depth)
        self.current_url = "Idle"
        self.logger = logger
        self.queue = queue # url queue
        self.parser = parser # page parser
        self.storage = storage # storage for storing data
        self.options = fetch_options()
        self.robots = {} # {"domain":[robotparser, urls since last]}


    def should_ignore(self, url):
        # Find a better method for staff like
        # static/greyindex.css?v=893e07cd07891c47f58b0a256b82ac7b
        for extension in self.options['crawler']['ignore-extensions'].split(','):
            if url.endswith("."+extension):
                return True
        return False


    def can_record(self):
        # store in a dict or array and after a number of urls remove it
        domain = url_to_domain(self.current_url)
        domains = list(self.robots.keys())
        if not domain in self.robots:
            self.robots[domain] = [gather_robots_txt(domain), 0]

        for robot_domain in domains:
            if robot_domain == domain:
                self.robots[robot_domain][1] = 0
                continue
            self.robots[robot_domain][1] += 1
            if self.robots[robot_domain][1] > int(self.options['crawler']['unload-robots']):
                del self.robots[robot_domain]

        if self.robots[domain][0]:
            return self.robots[domain][0].can_fetch(
                self.options['crawler']['user-agent-robots'],
                self.current_url
            )
        return True


    def run(self):
        while True:
            try:
                if not self.queue.empty():
                    item = self.queue.get()
                    self.work(item) # crawl the item
                else:
                    # Let the thread go idle until a new item comes up
                    # and set its status as Idle
                    self.current_url = "Idle"
                    sleep(1)
            except Exception:
                self.logger.exception('Worker::run')


    def work(self, queue_item):
        # queue_item[0] is the url, queue_item[1] is the depth
        self.current_url = queue_item[0]
        self.depth = queue_item[1]

        if len(queue_item) > 2:
            sleep(queue_item[2])
        try:
            if self.storage.record_url(self.current_url) and self.can_record():
                try:
                    self.req = urllib.request.Request(self.current_url,
                     headers={'User-Agent': self.options['crawler']['user-agent']})

                    self.url = urllib.request.urlopen(self.req)

                except urllib.error.HTTPError:
                    # we are going to wait a second when we try to reopen this
                    # url next time if we haven't done already ourselves
                    if not (len(queue_item) > 2):
                        self.queue.put((self.current_url, self.depth, 1))
                else:
                    url_content_type = self.url.info().get_content_type()
                    for allowed_content_type in self.options['crawler']['allow-content'].split(','):
                        if allowed_content_type in url_content_type:
                            break
                    else:
                        # Ignore the url that has any other content than
                        # the specified in the config
                        return

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
                        # self.logger.debug(str((fixed_url,url_validator(fixed_url),self.should_ignore(fixed_url))))
                        if not fixed_url:
                            # if url is empty '' no need to work with it
                            continue
                        if not url_validator(fixed_url):
                            # if url is invalid we can go on
                            continue
                        if self.should_ignore(fixed_url):
                            # if url is media or stylesheet we can go on
                            continue

                        if self.depth + 1 <= self.max_depth and self.storage.record_url(fixed_url):
                            # If the url doesnt exceed 2 depth and isn't already scanned
                            self.queue.put((fixed_url ,
                                            self.depth + 1)) # Add the url to the queue and increase the depth

        except Exception:
            self.logger.debug(self.current_url)
            self.logger.exception('Worker::work::exception')
