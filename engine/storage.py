# -*- coding: utf-8 -*-
import logging

from datetime import datetime, timedelta
from pymongo import MongoClient

from engine.config import fetch_options

class pymongo_recorder(object):

    def __init__(self, max_pool):
        self.options = fetch_options()
        CLIENT = MongoClient(self.options['mongo']['host'], int(self.options['mongo']['port']))
        self.lists = CLIENT[self.options['mongo']['database']][self.options['mongo']['index_list']]
        self.search = CLIENT[self.options['mongo']['database']][self.options['mongo']['retr_list']]

    def record_url(self, url):
        urls = self.lists.find({"url": str(url)})
        if urls.count() == 0:
            # If a url is not recorded, then we can crawl it
            return True
        if urls.count() == 1:
            time_passed = datetime.now() - urls[0]["time_scanned"] # get how much time
            # passed since this url was last scanned
            if time_passed > timedelta(days=int(self.options['mongo']['old_urls'])):
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
            logging.exception('Recorder-mongo-db')
