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

logging.basicConfig()


global SCANNED_ROBOTS
global SCANNED_HOSTS
global PROCESSES

SCANNED_ROBOTS = {}
SCANNED_HOSTS = []
PROCESSES = []

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

    def recorder_db(data, urls):
        # Database Update

        post = {"data": data, "urls": urls}
        posts = self.cursor_object.lists
        if posts.find({"data": str(data)}).count() == 0:
            try:
                posts.insert(post)
            except Exception:
                logging.exception('Recorder-mongo-db')
        else:
            try:
                post_list = posts.find({"data": str(data)})
                post_list["data"] = post_list["data"] + posts["data"]
                post_id = post_list["_id"]
                posts.update({"_id": post_id}, {"$set": post_list})
            except Exception:
                logging.exception('Recorder-mongo-db-Update')




class Crawler(object):
    def __init__(self, max_processes):
        self.queue = Queue()
        self.processes = {}
        for process in range(0, max_processes):
            self.processes[process] = Worker(self.queue)
            self.processes[process].start()
    def add_website(self, website_url):
        self.queue.put((website_url, 0))


class Worker(multiprocessing.Process):
    def __init__(self, queue):
        super(Worker, self).__init__()
        self.queue = queue
        self.parser = MyHTMLParser()
    def run(self):
        while True:
            item = self.queue.get()
            self.work(item)
            self.queue.task_done()
    def work(self, queue_item):
        self.parser.reset_list()
        self.req = urllib2.Request(queue_item[0])
        self.req.add_header('User-agent', 'Hurricane/0.1')
        try:
            self.url = urllib2.urlopen(req)
            self.data = self.url.read()
            self.urls = re.findall(r'href=[\'"]?([^\'" >]+)', data)
            self.parser.feed(self.data)

            self.data = "".join(self.parser.data_list)
            self.data = self.data.replace('\n', '')
            self.data = self.data.replace('\t', '')
            self.data = self.data.replace('\r', '')
            self.data = re.split(split_regex , self.data)
            for url in self.urls:
                self.queue.put((url, queue_item + 1))
        except:
            pass

"""
req = urllib2.Request('')
req.add_header('User-agent', 'Hurricane/0.1')
r = urllib2.urlopen(req)
data = r.read()
#pprint(re.findall(r'href=[\'"]?([^\'" >]+)', data))
parser = MyHTMLParser()
parser.reset_list()
parser.feed(data)
#pprint(parser.data_list)
data = "".join(parser.data_list)

data = data.replace('\n', '')
data = data.replace('\t', '')
data = data.replace('\r', '')

pprint(re.split(r"\s+", data))
#pprint(re.findall("(https?:\/\/)?([\da-z\.-]+)\.([a-zA-Z\.]{2,6})([\/\w \.-]*)*\/?", data))
"""