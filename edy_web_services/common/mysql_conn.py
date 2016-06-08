# -*- coding: utf-8 -*-
import pymysql


class mysqldb_conn():

    def __init__(self, host, port, db_name):
        self.db_host = host
        self.db_port = port
        self.db_name = db_name

    def conn(self):
        conn = pymysql.connect(host=self.db_host, user='esuser', passwd='Samp87Hj', db=self.db_name, port=self.db_port)
        return conn