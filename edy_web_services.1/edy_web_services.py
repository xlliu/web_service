# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import logging
import time

import pymongo
import pytz
import re
import xlsxwriter as xlsxwriter
from bson import ObjectId
from collections import OrderedDict
from flask import Flask, jsonify, g, send_from_directory, request

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
    logger.info("IP: %s" %request.remote_addr)
    g.mongo_collection = mongodb_conn("10.10.0.5", 27017, "xyt_survey_data_two", flag=0).conn()
    # g.mysql_conn = mysqldb_conn("10.10.0.9", 3306, "esuser").conn()
    

@app.teardown_request
def teardown_request(exception):
    if g.db is not None:
        g.db.close()
    # if g.mysql_conn is not None:
        # g.mysql_conn.close()

@app.route('/app/generator_excel/<int:version>_<string:pid>_<int:skip>_<int:limit>')
def generator_excel(version, pid, skip, limit):
    start = time.time()
    p = re.compile('^\d{10}$')

    def objectId_to_str(value):
        if isinstance(value, ObjectId):
            return str(value)
        if p.match(str(value)) if isinstance(value, long) else p.match(value):
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(value))
        return value

    _pid = "pid_%s" % pid
    document_project = getattr(g.mongo_collection, _pid)

    filepath = '/data/pywww/web_services/temp_excel/'
    # filepath = 'D:\\'
    filename = '%s.xlsx' % pid
    dpt_1 = document_project.find_one({"版本": version},{"_id": 0, "k_list": 1})

    dp = document_project.find({"版本": version},{"_id": 0, "v_list": 1, "k_list": 1}, no_cursor_timeout=True).skip(skip).limit(limit)
    workbook = xlsxwriter.Workbook(filepath + filename, {'constant_memory': True})
    worksheet = workbook.add_worksheet()
    #dpt = OrderedDict(sorted(dpt_1.items(),key=lambda d: d[0]))
    kl = dpt_1.get("k_list")[4:] if "用户" in dpt_1.get("k_list") else dpt_1.get("k_list")
    # kl.sort()
    worksheet.write_row(0, 0, kl)
    n = 1
    try:
        for v in dp:
            #si = sorted(v.iteritems(), key=lambda b: b[0])
            #kv = OrderedDict(si)
            # worksheet.write_row(n, 0, map(objectId_to_str, kv.values()))
            worksheet.write_row(n, 0, v.get("v_list")[4:] if "用户" in v.get("k_list") else v.get("v_list"))
            n += 1
        workbook.close()
    except Exception, e:
        print e
    end = time.time()
    print end - start

    return send_from_directory(filepath, filename, as_attachment=True)
    
    
@app.route('/app/generator_excel_zkey/<int:version>_<string:pid>_<int:skip>_<int:limit>')
def generator_excel_zkey(version, pid, skip, limit):
    start = time.time()
    p = re.compile('^\d{10}$')

    def objectId_to_str(value):
        if isinstance(value, ObjectId):
            return str(value)
        if p.match(str(value)) if isinstance(value, long) else p.match(value):
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(value))
        return value

    _pid = "pid_%s" % pid
    document_project = getattr(g.mongo_collection, _pid)

    filepath = '/data/pywww/web_services/temp_excel/'
    # filepath = 'D:\\'
    filename = '%s.xlsx' % pid
    dpt_1 = document_project.find_one({"版本": version},{"_id": 0})

    dp = document_project.find({"版本": version},{"_id": 0}, no_cursor_timeout=True).skip(skip).limit(limit)
    workbook = xlsxwriter.Workbook(filepath + filename, {'constant_memory': True})
    worksheet = workbook.add_worksheet()
    #dpt = OrderedDict(sorted(dpt_1.items(),key=lambda d: d[0]))
    k_top = ["开始时间", "结束时间", "用户", "序号", "版本"]
    kl = dpt_1.get("k_list")[4:] if "用户" in dpt_1.get("k_list") else dpt_1.get("k_list")
    
    # kl.sort()
    worksheet.write_row(0, 0, k_top + kl)
    n = 1
    try:
        for v in dp:
            #si = sorted(v.iteritems(), key=lambda b: b[0])
            #kv = OrderedDict(si)
            # worksheet.write_row(n, 0, map(objectId_to_str, kv.values()))
            vt = []
            vt.append(v.get(unicode("开始时间")))
            vt.append(v.get(unicode("结束时间")))
            vt.append(v.get(unicode("用户")))
            vt.append(v.get(unicode("序号")))
            vt.append(v.get(unicode("版本")))
            vt.extend(v.get("v_list")[4:] if "用户" in v.get("k_list") else v.get("v_list"))
            worksheet.write_row(n, 0, vt)
            n += 1
        workbook.close()
    except Exception, e:
        print e
    end = time.time()
    print end - start

    return send_from_directory(filepath, filename, as_attachment=True)


@app.route('/app/show_excel_info/<int:version>_<string:pid>_<int:skip>_<int:limit>')
def show_excel_info(version, pid, skip, limit):
    _pid = "pid_%s" % pid
    document_project = getattr(g.mongo_collection, _pid)
    # dpt_1 = document_project.find({"0d版本": version},{"_id": 0,"0d开始时间":0,"0d结束时间":0,"0d序号":0, "0d用户":0, "k_list": 0, "v_list": 0}).skip(skip).limit(limit)
    dpt_k = document_project.find_one({"版本": version},{"_id": 0, "k_list": 1})
    dpt_v = document_project.find({"版本": version},{"_id": 0, "v_list": 1, "k_list": 1}).skip(skip).limit(limit)
    # data_list = [f_dpt_1 for f_dpt_1 in dpt_1 if "k_list" not in f_dpt_1]
    dpt_value = []
    for dv in dpt_v:
        dpt_value.append(dv.get("v_list")[4:]) if u"用户" in dv.get("k_list") else dpt_value.append(dv.get("v_list"))
    data_list = [dpt_k.get("k_list")[4:] if u"用户" in dpt_k.get("k_list") else dpt_k.get("k_list")] + dpt_value
    # data_list_1 = []
    # for dv in dpt_1:
    #     if "k_list" in dv:
    #         data_list_1.append(dict(zip(dv["k_list"],dv["v_list"])))
    # logger.info("===============================")uu
    return jsonify({"data": data_list})

if __name__ == '__main__':
    app.run(port=5002)
