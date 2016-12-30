#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import zipfile


def construct_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(os.getcwd() + '/' + name + '.txt')
    logger.addHandler(handler)
    return logger


def zip_old_logs(logs_folder):
    # TODO: convert timestamp to a more readable form
    if os.path.exists(logs_folder+"/crawler.txt"):
        ct = str(os.stat(logs_folder+"/crawler.txt").st_ctime)
        with zipfile.ZipFile(logs_folder+"/"+ct+".zip", 'w') as myzip:
            myzip.write(logs_folder+"/crawler.txt")
            myzip.write(logs_folder+"/handlers.txt")
        os.remove(logs_folder+"/crawler.txt")
        os.remove(logs_folder+"/handlers.txt")
