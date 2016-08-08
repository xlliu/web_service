# -*- coding: utf-8 -*-
import md5
import sys
import uuid

reload(sys)
sys.setdefaultencoding('utf8')

import time

import re
import ConfigParser
import xlsxwriter as xlsxwriter
# import pandas as pd
from bson import ObjectId
from flask import Flask, jsonify, g, send_from_directory, request

from common.mongodb_conn import mongodb_conn
from common.utils import ConvertTime
from savReaderWriter.savWriter import SavWriter

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

config = ConfigParser.ConfigParser()  # 初始化config实例（建立一个空的数据集实例）
config.read("/data/pywww/web_services/edy_web_services.1/db.conf")  # 通过load文件filename来初始化config实例
# config.read("C:\Users\Administrator\PycharmProjects\web_service\edy_web_services.1\db.conf")  # 通过load文件filename来初始化config实例
db_1 = config.get("edy_web_services.1", "db_name_1")  # 获得指定section中的key的value
db_2 = config.get("edy_web_services.1", "db_name_2")
host = config.get("edy_web_services.1", "host")
port = config.getint("edy_web_services.1", "port")

logger.info("logging run start========================================>")


@app.before_request
def before_request():
    logger.info("IP: %s" % request.remote_addr)
    g.mongo_collection = mongodb_conn(host, port, db_1, flag=0).conn()
    g.mongo_collection_spss = mongodb_conn(host, port, db_2, flag=0).conn()
    # g.mysql_conn = mysqldb_conn("10.10.0.9", 3306, "esuser").conn()


@app.teardown_request
def teardown_request(exception):
    if g.db is not None:
        g.db.close()
        # if g.mysql_conn is not None:
        # g.mysql_conn.close()


@app.route('/app/exis_changelog/<string:pid>')
def exis_changelog(pid):
    _pid = "pid_%s" % pid
    document_project = getattr(g.mongo_collection, _pid)
    res = document_project.distinct(u"版本")
    return jsonify({"data": res})


@app.route('/app/generator_spss/<int:version>_<string:pid>')
def generator_spss(version, pid):
    filepath = '/data/pywww/web_services/temp_spss/'
    # filepath = 'd:\\'
    filename = '%s.sav' % pid
    fpn = filepath + filename
    _pid = "pid_%s" % pid
    document_project = getattr(g.mongo_collection_spss, _pid)
    vartitle = document_project.find_one({"版本": version}, {"_id": 0})

    vt = vartitle.get("k_pid")
    vty = vartitle.get("q_type")
    vo = [dict(zip([vot_ for vot_ in vot], [str(vot_) for vot_ in vot])) if isinstance(vot, list) else vot for vot in
          [dict(zip(v[0], v[1])) if v else None for v in vartitle.get("options")]]
    vs = vartitle.get("k_list")

    records = document_project.find({"版本": version}, {"_id": 0}, no_cursor_timeout=True)
    vr_t = []
    for v in records:
        user = uuid.uuid1(v.get("用户".decode('utf8')))
        starttime = ConvertTime.timestamp_2_time(v.get("开始时间".decode('utf8')))
        endtime = ConvertTime.timestamp_2_time(v.get("结束时间".decode('utf8')))
        changelog = v.get("版本".decode('utf8'))
        vr = v.get("v_list")
        vr = [user, starttime, endtime, changelog] + vr
        vr_t.append(vr)

    # resu = pd.DataFrame(vr_t)
    varNames = vt
    # varTypes = dict(zip(varNames, [50 if v.name == "object" else 0 for v in resu.dtypes.tolist()]))
    varTypes = dict(zip(varNames, [200 if v == "string" else 0 for v in vty]))
    varTypes["user"] = 200
    varTypes["starttime"] = 200
    varTypes["endtime"] = 200
    varTypes["changelog"] = 0

    varNames = ["user", "starttime", "endtime", "changelog"] + varNames
    vs = [u"用户", u"开始时间", u"结束时间", u"版本"] + vs
    # varTypes = dict(zip(varNames, [50]*len(varNames)))
    # va_temp = dict(zip(varNames, [{str(index+1): str(vvn) if isinstance(vvn, int) else vvn for index, vvn in enumerate(vn)} for vn in vo]))
    # # 清洗
    # [va_temp.pop(k) for k, v in va_temp.items() if not v.get("1")]
    # 倒排值
    # va_av_temp = {k: {v1: k1 for k1, v1 in v.items()} for k, v in va_temp.items()}
    varAttributes = {k: v for k, v in zip(vt, vo) if v}
    valueLabels = {k: v for k, v in zip(vt, vo) if v}
    varLabels = dict(zip(varNames, vs))
    ioUtf8 = True
    # missingValues = {'v4': "自动补齐"}
    # varNames = [k for k, v in zip(varNames, xrange(len(varNames)))]
    with SavWriter(savFileName=fpn, varNames=varNames, varTypes=varTypes,
                   varLabels=varLabels, valueLabels=valueLabels, ioUtf8=ioUtf8) as writer:
        try:
            writer.writerows(vr_t)
        except Exception as e:
            print e
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
    dpt_1 = document_project.find_one({"版本": version}, {"_id": 0})
    dp = document_project.find({"版本": version}, {"_id": 0}, no_cursor_timeout=True).skip(skip).limit(limit)
    workbook = xlsxwriter.Workbook(filepath + filename, {'constant_memory': True})
    worksheet = workbook.add_worksheet()
    k_top = ["开始时间", "结束时间", "用户", "序号", "版本"]
    kl = dpt_1.get("k_list")[4:] if "用户" in dpt_1.get("k_list") else dpt_1.get("k_list")
    worksheet.write_row(0, 0, k_top + kl)
    n = 1
    try:
        for v in dp:
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
    dpt_1 = document_project.find_one({"版本": version}, {"_id": 0})
    dp = document_project.find({"版本": version}, {"_id": 0}, no_cursor_timeout=True).skip(skip).limit(limit)
    workbook = xlsxwriter.Workbook(filepath + filename, {'constant_memory': True})
    worksheet = workbook.add_worksheet()
    k_top = ["开始时间", "结束时间", "用户", "序号", "版本"]
    kl = dpt_1.get("k_list")[4:] if "用户" in dpt_1.get("k_list") else dpt_1.get("k_list")
    worksheet.write_row(0, 0, k_top + kl)
    n = 1
    try:
        for v in dp:
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
    dpt_k = document_project.find_one({"版本": version}, {"_id": 0, "k_list": 1})
    dpt_v = document_project.find({"版本": version}, {"_id": 0, "v_list": 1, "k_list": 1}).skip(skip).limit(limit)
    dpt_value = []
    for dv in dpt_v:
        dpt_value.append(dv.get("v_list")[4:]) if u"用户" in dv.get("k_list") else dpt_value.append(dv.get("v_list"))
    data_list = [dpt_k.get("k_list")[4:] if u"用户" in dpt_k.get("k_list") else dpt_k.get("k_list")] + dpt_value
    return jsonify({"data": data_list})


if __name__ == '__main__':
    app.run(port=5002)
