# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient


class pymongo_recorder(object):

    def __init__(self, max_pool):
        CLIENT = MongoClient("127.0.0.1", 27017)
        self.lists = CLIENT['test']['lists']
        self.search = CLIENT['test']['search']
        self.scanned_urls = []

    def record_url(self, url):
        urls = self.lists.find({"url": str(url)})
        if urls.count() == 0:
            # If a url is not recorded, then we can crawl it
            self.scanned_urls.append(str(url))
            return True
        if urls.count() == 1:
            time_passed = datetime.now() - urls[0]["time_scanned"] # get how much time
            # passed since this url was last scanned
            if time_passed > timedelta(days=5): # if it is longer than 5 days
                return True

        return False

    def record_db(self, data, url):
        # Update the database with url and data
        try:
            data_list = {"data": data.encode('utf-8'), "url": url, "time_scanned": datetime.now()}
            list_result = self.lists.find({"url": url})
            if list_result.count() == 0:
                self.lists.insert(data_list)
            else:
                self.lists.update( # Update the time this url was scanned and allow a rescan
                    {'_id':list_result[0]['_id']},
                    {
                        "$set": {
                            "data": data.encode('utf-8'),
                            "urls": url,
                            "time_scanned": datetime.now()
                        }
                    }, upsert=False)
        except Exception:
            logging.exception('Recorder-mongo-db')