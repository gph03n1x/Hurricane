#!/usr/bin/env python
#Filename: crawler.py
#Author: johnpap
#PEP8 : NOT OK (Who cares anyway?)

MY_HOST = "127.0.0.1"
MY_DB = "test"

import re
import urllib2
import Queue
import multiprocessing
import logging
from pymongo import MongoClient
from pprint import pprint
from HTMLParser import HTMLParser
#from core.filters import *
#from core.utils import *
global SCANNED_ROBOTS
global SCANNED_HOSTS
global PROCESSES


SCANNED_ROBOTS = {}
SCANNED_HOSTS = []
PROCESSES = []

client = MongoClient(MY_HOST, 27017)
db = client[MY_DB]

logging.basicConfig(filename='error.log', level=logging.DEBUG)

url_regex = re.compile(r'href=[\'"]?([^\'" >]+)', re.VERBOSE | re.MULTILINE)
split_regex = re.compile(r'\s+', re.VERBOSE | re.MULTILINE)


class MyHTMLParser(HTMLParser):
    def reset_list(self):
        self.data_list = []
    def handle_data(self, data):
        self.data_list.append(data)


class pymongo_recorder(object):
    def __init__(self, cursor_object):
        self.cursor_object = cursor_object
        self.posts = self.cursor_object.lists
        self.urls = self.cursor_object.urls
    def record_url(self, url):
        if self.urls.find({"urls": str(url)}).count() == 0:
            self.urls.insert({"urls": str(url)})
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




class Crawler(object):
    def __init__(self, max_processes):
        self.manager = multiprocessing.Manager()
        self.queue = self.manager.Queue()
        self.processes = {}
        for process in range(0, max_processes):
            self.processes[process] = Worker(self.queue)
            #multiprocessing.freeze_support()
            self.processes[process].start()
    def add_website(self, website_url):
        self.queue.put((website_url, 0))
    def connect_processes(self, db):
        for process in self.processes:
            self.processes[process].connect_with_pymongo(db)


class Worker(multiprocessing.Process):
    def __init__(self, queue):
        super(Worker, self).__init__()
        self.queue = queue
        self.parser = MyHTMLParser()
        self.queue_item = None
    def connect_with_pymongo(self, db):
        self.pymongo = pymongo_recorder(db)
    def run(self):
        while True:
            try:
                if not self.queue.empty():
                    item = self.queue.get()
            except Exception:
                logging.exception('Worker-Exception-run()')
            else:
                self.work(item)
                self.queue.task_done()
    def work(self, queue_item):
        logging.info(str(queue_item))
        try:
            logging.info("ok - 0")
            if self.pymongo.record_url(queue_item[0]):
                logging.info("ok - 1")
                self.parser.reset_list()
                self.req = urllib2.Request(queue_item[0])
                self.req.add_header('User-agent', 'Hurricane/0.1')
                logging.info("ok - 2")
                self.url = urllib2.urlopen(req)
                self.data = self.url.read()
                self.urls = re.findall(url_regex, data)
                self.parser.feed(self.data)
                logging.info("ok - 3")
                logging.info(str(self.urls))
                self.data = "".join(self.parser.data_list)
                self.data = self.data.replace('\n', '')
                self.data = self.data.replace('\t', '')
                self.data = self.data.replace('\r', '')
                self.data = re.split(split_regex , self.data)
                logging.info("ok - 4")
                logging.info(str(self.data))
                for url in self.urls:
                    if queue_item[1] + 1 <= 2:
                        self.queue.put((url, queue_item[1] + 1))
                for data in self.data:
                    recorder_db(data, queue_item[0])
                logging.info("ok - 5")
        except Exception:
            logging.exception('Worker-Exception-work()')

if __name__ == '__main__':
    crawl = Crawler(2)
    crawl.connect_processes(db)
    crawl.add_website("http://koslib.com/")
