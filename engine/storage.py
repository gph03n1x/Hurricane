#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
# Third party libraries
import pymongo


class MongoDBRecorder(object):
    def __init__(self, logger, options):
        self.logger = logger
        self.options = options

        try:
            CLIENT = pymongo.MongoClient(self.options['mongo']['host'], int(self.options['mongo']['port']))
            self.lists = CLIENT[self.options['mongo']['database']][self.options['mongo']['data-collection']]
            self.search = CLIENT[self.options['mongo']['database']][self.options['mongo']['searches-collection']]
            self.db = CLIENT[self.options['mongo']['database']]
            self.lists.create_index( [("data", pymongo.TEXT)] )
            self.search.create_index( [("search", pymongo.TEXT)] )
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


    def _url_split(self, url):
        return url.split("//", 1)


    def record_url(self, url):
        protocol, url = self._url_split(url)
        # Check https: http:
        urls = self.lists.find({"url": str(url)})
        if urls.count() == 0:
            # If a url is not recorded, then we can crawl it
            return True
        if urls.count() == 1:
            # Count how much time passed since it was last scanned
            time_passed = datetime.now() - urls[0]["time_scanned"]
            # passed since this url was last scanned
            if time_passed > timedelta(days=int(self.options['mongo']['old-urls'])):
                return True
        return False


    def record_db(self, data, url, title, language):
        # Update the database with url and data
        try:
            protocol, url = self._url_split(url)
            data_list = {"data": data, "url": url, "title": title,
             "time_scanned": datetime.now(), "lang":language,
              "protocol":protocol}
            list_result = self.lists.find({"url": url})
            if list_result.count() == 0:
                self.lists.insert(data_list)
            else:
                # Update the time this url was scanned
                self.lists.update(
                    {'_id':list_result[0]['_id']},
                    {
                        "$set": {
                            "data": data,
                            "urls": url,
                            "time_scanned": datetime.now(),
                            "title": title,
                            "lang":language,
                            "protocol":protocol
                        }
                    }, upsert=False)
        except Exception:
            self.logger.exception('mongo_recorder::record_db')
