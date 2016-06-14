# -*- coding: utf-8 -*-
import logging
import time

import pymongo
import pytz
import re
import xlsxwriter as xlsxwriter
from bson import ObjectId
from collections import OrderedDict
from flask import Flask, jsonify, g, send_from_directory

from common.mongodb_conn import mongodb_conn
from common.mysql_conn import mysqldb_conn

app = Flask(__name__)

import logging
# 使用一个名字为fib的logger
logger = logging.getLogger('fib')
# 设置logger的level为DEBUG
logger.setLevel(logging.DEBUG)
# 创建一个输出日志到控制台的StreamHandler
hdr = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(name)s:%(levelname)s: %(message)s')
hdr.setFormatter(formatter)
# 给logger添加上handler
logger.addHandler(hdr)
logger.info("logging run start========================================>")


@app.before_request
def before_request():
    g.mongo_collection_edy = mongodb_conn("10.10.0.5", 27017, "xyt_survey", flag=0).conn()
    g.mysql_conn = mysqldb_conn("10.10.0.9", 3306, "esuser").conn()


@app.teardown_request
def teardown_request(exception):
    if g.db is not None:
        g.db.close()
    if g.mysql_conn is not None:
        g.mysql_conn.close()


@app.route('/app/weixin/five_list/<int:num>_<string:sort>')
def five_list(num=5, sort=""):
    tzchina = pytz.timezone('Asia/Shanghai')
    utc = pytz.timezone('UTC')
    document_project = g.mongo_collection_edy.xyt_survey_project
    cur = g.mysql_conn.cursor()
    result = document_project.find({"is_sendpacket": 1, "is_show_wx": {'$ne': 1}, "status": {"$ne": "-1"}).sort("publicdate", pymongo.DESCENDING).limit(num)
    text = {}
    temp_text = []
    for r in result:
        temp_list = {}
        temp_list["pid"] = r.get("short_id")
        temp_list["title"] = r.get("title")
        # temp_list["title"] = r.get("title")
        temp_list["is_sendpacket"] = r.get("is_sendpacket")
        temp_list["publicdate"] = r.get("publicdate").replace(tzinfo=utc).astimezone(tzchina).strftime(
            "%Y-%m-%d %H:%M:%S") if r.get("publicdate", "") else ""
        cur.execute('select mobile from ea_user where user_id=%s', r.get("creator_id"))
        temp_list["phone"] = cur.fetchone()[0]
        temp_text.append(temp_list)
    text["result"] = temp_text
    return jsonify(text)


if __name__ == '__main__':
    app.run(port=5001)
