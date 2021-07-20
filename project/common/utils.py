# -*- coding: utf-8 -*-

import os
import datetime
import time
import inspect
from xpinyin import Pinyin

__author__ = "liuxu"


# dict转为class
class Dict2Class(dict):
    def __init__(self, *args, **kwargs):
        super(Dict2Class, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Dict2Class, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Dict2Class, self).__delitem__(key)
        del self.__dict__[key]


# 转化日期为数字(YYMMDD)
def date2num(date):
    return int('{}{:0>2d}{:0>2d}'.format(str(date.year)[2:4],
                                         date.month,
                                         date.day))


# 时间戳转日期
def ts2dt(timestamp):
    timeArray = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", timeArray)


# 日期转时间戳
def dt2ts(dt):
    return time.mktime(dt.timetuple())


# 日期转字符串
def dt2str(dt=None):
    if not dt:
        dt = datetime.datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')


# 取得当前时间
def get_now():
    return datetime.datetime.now()


# 取得月份中的最后一天
def month_last_day(dt):
    next_month = dt.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)


# 获取两日期之间的每一天
def get_everyday(start_datetime, end_datetime):
    dates = []
    while start_datetime <= end_datetime:
        dates.append(start_datetime)
        start_datetime += datetime.timedelta(days=1)

    return dates


# 取得日期增加指定天数后的日期（默认增加一天）
def add_days(dt, days=1):
    return dt + datetime.timedelta(days=days)


# 取得触发名（类名.方法名）
def get_trigger(obj):
    return '{cls}.{func}'.format(cls=obj.__class__.__name__,
                                 func=inspect.stack()[1][3])


# 判断是否含有汉字
def check_contain_chinese(check_str):
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


# 生成模糊查询字符串
def get_fuzzy(keyword):
    return "%{}%".format(keyword.replace('%', '\%').replace('_', '\_'))


# list转dict（[{'timestamp': 10028490, 'value': 100}] -> {10028490: 100}）
def list2dict(data, key, value):
    return {item.get(key, ''): item.get(value, '') for item in data}


# dict转list（{10028490: 100} -> [{'timestamp': 10028490, 'value': 100}]）
def dict2list(data, key, value):
    return [{key: k, value: v} for k, v in data.items()]


# 取得汉字的拼音首字母
def get_pinyin(value):
    pinyin = Pinyin()
    return pinyin.get_initials(value, '').upper()


# 删除文件夹下所有文件
def del_files(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_files(c_path)
        else:
            os.remove(c_path)
