#!/usr/bin/env python
# -*-  coding:utf-8 -*-

"""
@version: 1.0.0
@author: xlliu
@contact: liu.xuelong@163.com
@site: https://github.com/xlliu
@software: PyCharm
@file: utils.py
@time: 2016/8/8 19:05
"""
import time


class ConvertTime(object):

    """
        About time convert
    """

    @staticmethod
    def time_2_timestamp(time, **kwargs):

        time_frame = kwargs.get("timeframe", "%Y-%m-%d %H:%M:%S")
        # a = "2013-10-10 23:40:00"
        time_array = time.strptime(time, time_frame)
        # 转换为时间戳:
        time_stamp = int(time.mktime(time_array))
        return time_stamp

    @staticmethod
    def timestamp_2_time(timestamp, **kwargs):
        time_frame = kwargs.get("timeframe", "%Y-%m-%d %H:%M:%S")
        # a = "2013-10-10 23:40:00"
        time_array = time.localtime(timestamp)
        time_str = time.strftime(time_frame, time_array)
        return time_str