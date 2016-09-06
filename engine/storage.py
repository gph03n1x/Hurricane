#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient
from engine.config import fetch_options


class MongoDBRecorder(object):
    def __init__(self, logger):
        self.options = fetch_options()
        self.logger = logger
        try:
            CLIENT = MongoClient(self.options['mongo']['host'], int(self.options['mongo']['port']))
            self.lists = CLIENT[self.options['mongo']['database']][self.options['mongo']['data-collection']]
            self.search = CLIENT[self.options['mongo']['database']][self.options['mongo']['searches-collection']]
        except Exception as mongo_error:
            print("[-] Database Error , exitting ...")
            self.logger.exception("mongo_recorder::__init__")
            exit()


    def get_lists_collection(self):
        return self.lists


    def get_search_collection(self):
        return self.search


    def record_search(self, search_string):
        record = {"search": search_string}
        if self.search.find(record).count() == 0:
            self.search.insert(record)


    def record_url(self, url):
        urls = self.lists.find({"url": str(url)})
        if urls.count() == 0:
            # If a url is not recorded, then we can crawl it
            return True
        if urls.count() == 1:
            time_passed = datetime.now() - urls[0]["time_scanned"] # get how much time
            # passed since this url was last scanned
            if time_passed > timedelta(days=int(self.options['mongo']['old-urls'])):
                return True
        return False


    def record_db(self, data, url):
        # Update the database with url and data
        try:
            data_list = {"data": data, "url": url, "time_scanned": datetime.now()}
            list_result = self.lists.find({"url": url})
            if list_result.count() == 0:
                self.lists.insert(data_list)
            else:
                self.lists.update( # Update the time this url was scanned and allow a rescan
                    {'_id':list_result[0]['_id']},
                    {
                        "$set": {
                            "data": data,
                            "urls": url,
                            "time_scanned": datetime.now()
                        }
                    }, upsert=False)
        except Exception:
            self.logger.exception('mongo_recorder::record_db')
