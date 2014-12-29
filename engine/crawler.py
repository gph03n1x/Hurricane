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
#global CLIENT

SCANNED_ROBOTS = {}

logging.basicConfig(filename='error.log', level=logging.DEBUG)

url_regex = re.compile(r'href=[\'"]?([^\'" >]+)', re.VERBOSE | re.MULTILINE)
split_regex = re.compile(r'\s+', re.VERBOSE | re.MULTILINE)


class MyHTMLParser(HTMLParser):
    def reset_list(self):
        self.data_list = []
    def handle_data(self, data):
        self.data_list.append(data)


class pymongo_recorder(object):
    def __init__(self, CLIENT):
        #CLIENT = MongoClient(MY_HOST, 27017)
        #self.cursor_object = CLIENT['test']['lists']
        logging.debug('rec - init')
        self.posts = CLIENT['test']['lists']
        self.urls = CLIENT['test']['urls']
        logging.debug('rec - ok - complete')
    def record_url(self, url):
        logging.debug('rec - 1')
        if self.urls.find({"urls": str(url)}).count() == 0:
            self.urls.insert({"urls": str(url)})
            logging.debug('rec - 2')
            return True
        return False


    def recorder_db(self, data, urls):
        # Database Update
        logging.debug('rec - 3')
        post = {"data": data, "urls": urls}
        if self.posts.find({"data": str(data)}).count() == 0:
            logging.debug('rec - 4')
            try:
                self.posts.insert(post)
            except Exception:
                logging.exception('Recorder-mongo-db')
        else:
            logging.debug('rec - 5')
            try:
                post_list = self.posts.find({"data": str(data)})
                post_list["data"] = post_list["data"] + post["data"]
                post_id = post_list["_id"]
                self.posts.update({"_id": post_id}, {"$set": post_list})
            except Exception:
                logging.exception('Recorder-mongo-db-Update')





class Crawler(object):
    def __init__(self, max_processes):
        self.queue = multiprocessing.Queue()
        self.processes = {}
        for process in range(0, max_processes):
            print process
            self.processes[process] = Worker(self.queue)
            self.processes[process].start()
    def add_website(self, website_url):
        self.queue.put((website_url, 0))


class Worker(multiprocessing.Process):
    def __init__(self, queue):
        super(Worker, self).__init__()
        self.queue = queue
        self.parser = MyHTMLParser()
        self.queue_item = None
        logging.info("init - ok")
        self.pymongo_oop = pymongo_recorder(MongoClient(MY_HOST, 27017))
        logging.info("init - ok - complete")
    def run(self):
        while True:
            try:
                logging.info("init - run - 1")
                if not self.queue.empty():
                    item = self.queue.get()
                    self.work(item)
                logging.info("init - run - 2")
            except Exception:
                logging.exception('Worker-Exception-run()')
                logging.info(str(self.queue.empty()))
    def work(self, queue_item):
        logging.info(str(queue_item))
        try:
            logging.info("ok - 0")
            if self.pymongo_oop.record_url(queue_item[0]):
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
                    self.pymongo_oop.recorder_db(data, queue_item[0])
                logging.info("ok - 5")
        except Exception:
            logging.exception('Worker-Exception-work()')

if __name__ == '__main__':
    crawl = Crawler(1)
    crawl.add_website("http://koslib.com/")
