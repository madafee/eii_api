# -*- coding: utf-8 -*-

import datetime
from functools import partial
from flask_restful import reqparse
from project.common import schema

__author__ = "liuxu"


# 自定义字段解析
class RequestParser(reqparse.RequestParser):
    def __init__(self):
        super(RequestParser, self).__init__()

    # 增加解析字段（默认为必有且不能为空）
    def add_body(self, name, required=True, nullable=False,
                 store_missing=False, **kwargs):
        # 含有选定值，则默认类型为数值型
        if kwargs.get('choices') and not kwargs.get('type'):
            kwargs['type'] = int

        # 若有默认值，为空时使用默认值
        if kwargs.get('default'):
            store_missing = True

        # 若为数组，默认数组可以为空
        if kwargs.get('action') == 'append':
            nullable = True
            required = False
            kwargs['default'] = []
            store_missing = True

        self.add_argument(name,
                          required=required,
                          nullable=nullable,
                          store_missing=store_missing,
                          **kwargs)


# 自定义request参数格式
class Type(object):
    @staticmethod
    def _get_integer(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError('{} is not a valid integer'.format(value))

    @staticmethod
    def _get_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            raise ValueError('{} is not a valid float'.format(value))

    # float
    @staticmethod
    def positive_decimal(value, argument='argument'):
        value = Type._get_float(value)
        if value < 0.0:
            error = ('Invalid {0}: {1}. {0} must be a non-positive-decimal '
                     .format(argument, value))
            raise ValueError(error)
        return value

    # 自然数(0, 1, 2, 3...)
    @staticmethod
    def natural(value, argument='argument'):
        value = Type._get_integer(value)
        if value < 0:
            error = ('Invalid {0}: {1}. {0} must be a non-negative '
                     .format(argument, value))
            raise ValueError(error)
        return value

    # 正数(1, 2, 3...)
    @staticmethod
    def positive(value, argument='argument'):
        value = Type._get_integer(value)
        if value < 1:
            error = ('Invalid {0}: {1}. {0} must be a positive integer'
                     .format(argument, value))
            raise ValueError(error)
        return value

    # 日期(YYYY-MM-DD)
    @staticmethod
    def date(value, argument='argument'):
        if not value:
            raise ValueError('{} is null'.format(argument))

        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            raise ValueError('{}({}) is invalid'.format(argument, value))

    # 日期时间
    @staticmethod
    def datetime(value, argument='argument'):
        if not value:
            raise ValueError('{} is null'.format(argument))

        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except Exception:
            raise ValueError('{}({}) is invalid'.format(argument, value))

    # 不为空
    @staticmethod
    def notnull(value, argument='argument'):
        if value is None:
            raise ValueError('{} is null'.format(argument))

        return value

    # 布尔（1/0, true/false）
    @staticmethod
    def boolean(value, argument='argument'):
        if isinstance(value, bool):
            return value

        if not value:
            raise ValueError('{} is null'.format(argument))
        value = value.lower()
        if value in ('true', '1',):
            return True
        if value in ('false', '0',):
            return False
        raise ValueError("Invalid {} for boolean: {}".format(argument, value))

    # JSON
    @staticmethod
    def _json(value, format, argument='argument'):
        return schema.Json.check(value, format)

    @staticmethod
    def json(format):
        return partial(Type._json, format=format)
