#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import urllib.error
import asyncio
# Third party libraries
import aiohttp
# Engine libraries
from engine.filters import *
from engine.utils import gather_robots_txt
from engine.parser import PageParser
from engine.storage import MongoDBRecorder
from engine.utils import construct_logger


class Crawler(threading.Thread):
    def __init__(self, options):
        super(Crawler, self).__init__()
        self.addToQueue = []
        self.queue = asyncio.Queue()
        self.threads = {}
        self.options = options
        self.max_threads = self.options["crawler"]["threads"]
        self.logger = construct_logger("data/logs/crawler")
        self.storage = MongoDBRecorder(self.logger, self.options)
        self.parser = PageParser(self.logger, self.options)
        self.loop = None

    def get_storage(self):
        """
        Returns the storage associated with the crawler
        :return: engine.storage.MongoDBRecorder object
        """
        return self.storage

    def get_logger(self):
        """
        Returns the logger associated with the crawler
        :return: logging.Logger object
        """
        return self.logger

    def add_website(self, website_url):
        """
        Adding a web page to addToQueue List in order
        to add it asynchronously when a worker will go Idle
        :param website_url:
        :return:
        """
        if url_validator(website_url):
            # Add a url in the queue
            self.addToQueue.append((remove_backslash(website_url), 0))

    async def need_update(self):
        pass

    def run(self):
        """
        Constructs an event loop and adds a number of workers
        :return:
        """
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        tasks = []
        self.threads[0] = Worker(self, 0, self.options, self.logger,
                                 self.queue, self.storage, self.parser, self.addToQueue, role=1)
        tasks.append(self.threads[0].begin())
        for thread in range(1, self.max_threads):
            # Spawn and start the threads
            self.threads[thread] = Worker(self, thread, self.options, self.logger,
                                          self.queue, self.storage, self.parser, self.addToQueue)
            tasks.append(self.threads[thread].begin())
        self.loop.run_until_complete(asyncio.gather(*tasks))


class Worker:
    def __init__(self, crawler, id, options, logger, queue, storage, parser, addtoq, role=0):
        self.id = id
        self.crawler = crawler
        self.addToQ = addtoq
        self.options = options
        self.max_depth = self.options["crawler"]["depth"]
        self.current_url = "Idle"
        self.logger = logger
        self.queue = queue  # url queue
        self.parser = parser  # page parser
        self.storage = storage  # storage for storing data
        self.robots = {}  # {"domain":[ robotparser, urls since last]}
        self.keep_pulling = True
        self.role = role

    def getStatus(self):
        pass

    def is_idle(self) -> bool:
        return self.current_url == "Idle"

    def can_record(self):
        # store in a dict or array and after a number of urls remove it
        domain = url_to_domain(self.current_url)
        domains = list(self.robots.keys())
        if domain not in self.robots:
            self.robots[domain] = [gather_robots_txt(domain), 0]

        for robot_domain in domains:
            if robot_domain == domain:
                self.robots[robot_domain][1] = 0
                continue
            self.robots[robot_domain][1] += 1
            if self.robots[robot_domain][1] > self.options['crawler']['unload-robots']:
                del self.robots[robot_domain]

        if self.robots[domain][0]:
            return self.robots[domain][0].can_fetch(
                self.options['crawler']['user-agent-robots'],
                self.current_url
            )
        return True

    async def begin(self):
        while self.keep_pulling:
            try:

                if self.role == 1 and len(self.addToQ) > 0:
                    pending_q = self.addToQ.pop()
                    await self.queue.put(pending_q)

                if not self.queue.empty():
                    item = await self.queue.get()
                    await self.work(item)  # crawl the item
                else:
                    # Let the thread go idle until a new item comes up
                    # and set its status as Idle
                    self.current_url = "Idle"
                    await asyncio.sleep(1)
            except Exception:
                self.logger.exception('Worker::run')

    async def work(self, queue_item):
        # queue_item[0] is the url, queue_item[1] is the depth

        self.current_url = queue_item[0]


        for thread in self.crawler.threads:
            # Checking if any other worker is already
            # waiting for a response on the same url
            if thread == self.id:
                # Ignore the same worker.
                continue
            if self.crawler.threads[thread].current_url == queue_item[0]:
                # Since one is already working then
                # we return to exit the method
                return

        depth = queue_item[1]
        if len(queue_item) > 2:
            await asyncio.sleep(queue_item[2])
        try:
            if self.storage.check_url(self.current_url) and self.can_record():
                self.logger.debug("Crawling: " + self.current_url)
                try:
                    session = aiohttp.ClientSession(
                     headers={'User-Agent': self.options['crawler']['user-agent']}
                    )
                    self.url = await session.get(self.current_url)
                except urllib.error.URLError:
                    # Closing the request and the session
                    self.url.close()
                    session.close()
                except urllib.error.HTTPError:
                    # Closing the request and the session
                    self.url.close()
                    session.close()
                    # we are going to wait a second when we try to reopen this
                    # url next time if we haven't done already ourselves
                    # self.logger.error("HTTPError: " + self.current_url)
                    if not (len(queue_item) > 2):
                        await self.queue.put((self.current_url, depth, 1))
                else:
                    # self.logger.debug("Done: " + self.current_url)
                    url_content_type = self.url.headers['content-type']
                    for allowed_content_type in self.options['crawler']['allow-content'].split(','):
                        if allowed_content_type in url_content_type:
                            break
                    else:
                        # Ignore the url that has any other content than
                        # the specified in the config
                        return
                    self.data = await self.url.read()
                    # Closing the request and the session
                    self.url.close()
                    session.close()
                    self.urls = self.parser.pull_urls(self.data)  # Fetch all urls from the webpage
                    #self.urls = filter(None, self.urls)
                    try: # If the webpage has a charset set
                        # Parse a decoded webpage
                        self.data, title, language = self.parser.parse_page(self.data.lower())
                    except (TypeError, UnicodeDecodeError):
                        # If an exception is raised
                        # parsing with utf-8 decoded
                        self.data, title, language  = self.parser.parse_page(self.data.decode('utf-8').lower())

                    # Record the results
                    self.storage.record_db(self.data, self.current_url, title, language)

                    # Add the urls found in the webpage
                    for url in self.urls:
                        fixed_url = complete_domain(crop_fragment_identifier(url), self.current_url)
                        if not fixed_url:
                            # if url is empty '' no need to work with it
                            continue
                        if not url_validator(fixed_url):
                            # if url is invalid we can go on
                            continue

                        if depth + 1 <= self.max_depth and self.storage.check_url(fixed_url):
                            # If the url doesnt exceed depth
                            # and isn't already scanned
                            # Add the url to the queue and increase the depth
                            await self.queue.put((fixed_url ,
                                            depth + 1))

        except Exception:
            self.logger.debug(self.current_url)
            self.logger.exception('Worker::work::exception')
