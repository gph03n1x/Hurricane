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

class MyHTMLParser(HTMLParser):
    def reset_list(self):
        self.data_list = []
        self.lock = True

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.lock = False

    def handle_data(self, data):
        if self.lock is False:
            self.data_list.append(data)

class pymongo_recorder(object):
    def __init__(self, max_pool):
        CLIENT = MongoClient("127.0.0.1", 27017, max_pool_size=max_pool)
        self.posts = CLIENT['test']['lists']
        self.urls = CLIENT['test']['urls']
        self.scanned_urls = []

    def record_url(self, url):
        if self.urls.find({"urls": str(url)}).count() == 0:
            self.urls.insert({"urls": str(url)})
            self.scanned_urls.append(str(url))
            return True
        return False

    def recorder_db(self, data, urls):
        # Database Update
        post = {"data": data, "urls": urls}
        if self.posts.find({"data": str(data)}).count() == 0:
            try:
                self.posts.insert(post)
            except Exception:
                logging.exception('Recorder-mongo-db')
        else:
            try:
                post_list = self.posts.find({"data": str(data)})
                post_list["data"] = post_list["data"] + post["data"]
                post_id = post_list["_id"]
                self.posts.update({"_id": post_id}, {"$set": post_list})
            except Exception:
                logging.exception('Recorder-mongo-db-Update')

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
        self.file_object = pymongo_recorder(self.max_processes)

    def add_website(self, website_url):
        self.queue.put((website_url, 0))

    def begin(self):
        for process in range(0, self.max_processes):
            self.processes[process] = Worker(self.queue, self.file_object)
            self.processes[process].start()

class Worker(threading.Thread):
    def __init__(self, queue, file_object):
        super(Worker, self).__init__()
        self.queue = queue
        self.file_object = file_object
        self.parser = MyHTMLParser()
        self.queue_item = None

    def run(self):
        while True:
            try:
                if not self.queue.empty():
                    item = self.queue.get()
                    self.work(item)
                else:
                    sleep(1)
            except Exception:
                logging.exception('Worker-Exception-run()')

    def work(self, queue_item):
        logging.info(str(queue_item))
        try:
            if self.file_object.record_url(queue_item[0]):
                self.parser.reset_list()
                self.req = urllib2.Request(queue_item[0])
                self.req.add_header('User-agent', 'Hurricane/0.1')
                self.url = urllib2.urlopen(self.req)
                self.data = self.url.read()
                self.encoding = self.url.headers.getparam('charset')
                self.urls = re.findall(url_regex, self.data)
                if type(self.encoding) != None and len(self.encoding) > 0:
                    self.parser.feed(self.data.decode(self.encoding))
                else:
                    self.parser.feed(self.data)
                self.data = "".join(self.parser.data_list)
                self.data = re.sub("(\\n|\\t|\\r)" , "", self.data)
                for url in self.urls:
                    pprint(url)
                    if queue_item[1] + 1 <= 2 and (not (url in self.file_object.scanned_urls)):
                        self.queue.put((url, queue_item[1] + 1))
                self.file_object.recorder_db(self.data.lower(), queue_item[0])
        except Exception:
            logging.exception('Worker-Exception-work()')

if __name__ == '__main__':
    crawl = Crawler(1)
    crawl.add_website("http://koslib.com/")
    crawl.begin()
