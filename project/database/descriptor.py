# -*- coding: utf-8 -*-

import json
from project.common import datadictionary as dd
from project.common import exception as ex
from project.database import models
from project.common import schema

__author__ = "liuxu"


# 描述器类
class DataDictionary(object):
    def __init__(self, name, dictionary):
        self.name = name
        self.dictionary = dictionary

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            if instance.__dict__.get(self.name):
                return self.dictionary.get(instance.__dict__[self.name])


class Record(object):
    def __init__(self, name, table):
        self.name = name
        self.table = table

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            if instance.__dict__.get(self.name):
                return self.table.get(instance.__dict__.get(self.name))


class Json(object):
    def __init__(self, name, format):
        self.name = name
        self.format = format

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return json.loads(instance.__dict__[self.name])

    def __set__(self, instance, value):
        schema.Json.check(value, self.format)
        setattr(instance, self.name, json.dumps(value))


class User(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            if instance.__dict__.get(self.name):
                return models.TblUser.get(instance.__dict__[self.name]).name
