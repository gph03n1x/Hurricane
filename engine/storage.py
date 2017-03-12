#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
# Third party libraries
import elasticsearch
# Engine libraries
from engine.filters import remove_protocol
from engine.config import get_commit_hash


class ElasticRecorder:
    def __init__(self, logger, options):
        self.elastic_search = elasticsearch.Elasticsearch()
        self.logger = logger
        self.options = options
        self.version_hash = get_commit_hash()
        self.elastic_search.indices.create(index='web_page', ignore=400)
        self.elastic_search.indices.create(index='user_search', ignore=400)

    def get_lists_collection(self):
        """
        Returns the lists collection
        :return:
        """
        # TODO: use lambdas here maybe ?
        return self

    def get_search_collection(self):
        """
        Returns the search collection
        :return:
        """
        return self.elastic_search

    def record_words(self, words):
        """
        Records a list of words in the suggestion.
        :return:
        """


    def record_search(self, search):
        """
        Records a search input.
        :param search:
        :return:
        """
        data_list = {'search': search}
        duplicates = self.elastic_search.search(index="user_search", doc_type="user_search",
                                                body={
                                                    "query": {
                                                        "term": {'search': search}
                                                    }
                                                })

        if duplicates['hits']['total'] == 0:
            res = self.elastic_search.index(index="user_search", doc_type="user_search", body=data_list)


    def check_url(self, url):
        """
        Checks if a url is already crawled.
        :param url:
        :return:
        """
        protocol, url = remove_protocol(url)
        # Check https: http:
        duplicates = self.elastic_search.search(index="web_page", doc_type="web_page",
                                                   body={
                                                       "query": {
                                                           "term": { "url": url}
                                                       }
                                                   })

        if duplicates['hits']['total'] == 0:
            # If a url is not recorded, then we can crawl it
            return True
        if duplicates['hits']['total'] == 1:
            #return True
            # Count how much time passed since it was last scanned
            time_passed = datetime.now() - duplicates['hits']['hits'][0]["_source"]["time_scanned"]
            # Get the version hash
            version = duplicates['hits']['hits'][0]["_source"]["hash_version"]

            if time_passed > timedelta(days=int(self.options['mongo']['old-urls'])) or self.version_hash != version:
                return True

        return False

    def record_db(self, data, url, title, language):
        """
        Records information about a crawled website at the db
        :param data:
        :param url:
        :param title:
        :param language:
        :return:
        """
        try:
            protocol, url = remove_protocol(url)
            data_list = {"data": data, "url": url, "title": title,
                         "time_scanned": datetime.now(), "lang": language,
                         "protocol": protocol, 'hash_version': self.version_hash}

            duplicates = self.elastic_search.search(index="web_page", doc_type="web_page",
                                                       body={
                                                           "query": {
                                                               "term":  {"url": url}
                                                           }
                                                       })

            if duplicates['hits']['total'] == 0:
                res = self.elastic_search.index(index="web_page", doc_type='web_page', body=data_list)
            else:
                # Update the time this url was scanned
                # del data_list['url']
                self.elastic_search.update(index="web_page", doc_type='web_page', id=duplicates['hits']['hits'][0]['_id'],
                            body={"doc": data_list})

        except Exception:
            # self.logger.debug(data_list)
            self.logger.exception('ElasticRecorder::record_db')
