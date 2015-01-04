# -*- coding: utf-8 -*-

import re
import string
import urllib2
import logging
import codecs
import multiprocessing
import threading
from time import sleep
from pprint import pprint
from HTMLParser import HTMLParser
from pymongo import MongoClient

global SCANNED_ROBOTS
SCANNED_ROBOTS = {}

logging.basicConfig(filename='error.log', level=logging.DEBUG)

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


class pymongo_recorder(object):

    def __init__(self, max_pool):
        CLIENT = MongoClient("127.0.0.1", 27017, max_pool_size=max_pool)
        self.posts = CLIENT['test']['lists']
        self.urls = CLIENT['test']['urls']
        self.scanned_urls = []

    def record_url(self, url):
        if self.urls.find({"urls": str(url)}).count() == 0:
            # If a url is not recorded, record it so that the crawler
            # will not scan it again
            self.urls.insert({"urls": str(url)})
            self.scanned_urls.append(str(url))
            return True
        return False

    def recorder_db(self, data, urls):
        # Update the database with url and data
        try:
            post = {"data": data, "urls": urls}
            self.posts.insert(post)
        except Exception:
            logging.exception('Recorder-mongo-db')


class file_storage(object):

    def __init__(self):
        try:
            self.urls_file = codecs.open("urls.txt", "r", "utf-8")
            self.scanned_urls = self.urls_file.read().split("\n")
            self.urls_file.close()
        except IOError:
            self.scanned_urls = []

    def record_url(self, url):
        if not (url in self.scanned_urls):
            string_construct = "%s\n" % (url)
            self.urls_file_append = codecs.open("urls.txt", "a", "utf-8")
            self.urls_file_append.write(string_construct)
            self.urls_file_append.close()
            self.scanned_urls.append(url)
            return True
        return False

    def recorder_db(self, data, url):
        self.data_file = codecs.open("data.txt", "a", "utf-8")
        string_construct = "%s:%s\n" % (data.lower(), url)
        self.data_file.write(string_construct)
        self.data_file.close()


class Crawler(object):

    def __init__(self, max_processes):
        self.queue = multiprocessing.Queue()
        self.processes = {}
        self.max_processes = max_processes
        # Create a data storage for the threads to use
        self.file_object = pymongo_recorder(self.max_processes)

    def add_website(self, website_url):
        self.queue.put((website_url, 0)) # Add a url in the queue

    def begin(self):
        for process in range(0, self.max_processes):
            # Spawn and start the threads
            self.processes[process] = Worker(self.queue, self.file_object)
            self.processes[process].start()


class Worker(threading.Thread):

    def __init__(self, queue, file_object):
        super(Worker, self).__init__()
        self.queue = queue
        self.file_object = file_object # file_object is the storage the crawler
                                       # will use .
        self.parser = MyHTMLParser()

    def run(self):
        while True:
            try:
                if not self.queue.empty():
                    item = self.queue.get()
                    self.work(item) # crawl the item
                else:
                    sleep(1) # Let the thread go idle until a new item comes up
            except Exception:
                logging.exception('Worker-Exception-run()')

    def work(self, queue_item):
        # queue_item[0] is the url, queue_item[1] is the depth
        logging.info(str(queue_item))
        try:
            if self.file_object.record_url(queue_item[0]):
                self.parser.reset_list()

                self.req = urllib2.Request(queue_item[0]) # Start a url request
                self.req.add_header('User-agent', 'Hurricane/0.1')
                self.url = urllib2.urlopen(self.req)
                self.data = self.url.read() # Fetch the data from the webpage
                self.encoding = self.url.headers.getparam('charset') # Fetch
                self.urls = re.findall(url_regex, self.data) # Fetch all urls from the webpage

                if type(self.encoding) != None: # If the webpage has a charset set
                    self.parser.feed(self.data.decode(self.encoding)) # Parse a decoded webpage
                else:
                    self.parser.feed(self.data) # Parse the webpage as it is
                self.data = "".join(self.parser.data_list) # get all the data in a long string

                self.data = re.sub(escape_regex , "", self.data) # Remove unnecessary escape characters
                self.data = re.sub(split_regex , " ", self.data) # Replace html spaces with only one
                self.file_object.recorder_db(self.data.lower(), queue_item[0]) # Record the results
                # Add the urls found in the webpage
                for url in self.urls:
                    if queue_item[1] + 1 <= 2 and (not (url in self.file_object.scanned_urls)):
                        # If the url doesnt exceed 2 depth and isn't already scanned
                        pprint(url)
                        self.queue.put((url, queue_item[1] + 1)) # Add the url to the queue and increase the depth

        except Exception:
            logging.exception('Worker-Exception-work()')

if __name__ == '__main__':
    crawl = Crawler(2)
    crawl.add_website("http://koslib.com/")
    crawl.begin()
