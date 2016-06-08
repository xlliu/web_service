# -*- coding: utf-8 -*-
import pymongo
from flask import g


class mongodb_conn():
    def __init__(self, host, port, collection, flag=0):
        self.db_host = host
        self.db_port = port
        self.db_collection = collection
        self.db_flag = flag

    def conn(self):
        g.db = pymongo.MongoClient(self.db_host, self.db_port)
        collection = g.db[self.db_collection]
        if self.db_flag:
            collection.authenticate("surpro", "Gmtinter89")
        return collection
