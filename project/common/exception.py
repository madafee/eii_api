# -*- coding: utf-8 -*-

__author__ = "liuxu"
# 自定义异常


class CustomError(Exception):
    def __init__(self, return_code, info=None):
        self.return_code = return_code
        self.info = info

    def __str__(self):
        return repr(self.info) if self.info else ''


# 返回错误
class ReturnError(CustomError):
    def __init__(self, return_code, info=None):
        self.return_code = return_code
        self.info = info

    def __str__(self):
        return repr(self.info) if self.info else ''


# 记录不存在
class NonRecordError(CustomError):
    def __init__(self, info):
        self.return_code = 'RECORD_NOT_FOUND'
        self.info = info

    def __str__(self):
        return repr('{} is not exist!'.format(self.info))


# 字典值不存在
class NonDictionaryError(CustomError):
    def __init__(self, dict_name, dict_value):
        self.return_code = 'DICTIONARY_NOT_FOUND'
        self.dict_name = dict_name
        self.dict_value = dict_value

    def __str__(self):
        return repr('{}({}) is not exist!'.format(self.dict_name,
                                                  self.dict_value))


# 数据格式不正确
class FormatError(CustomError):
    def __init__(self, info):
        self.return_code = 'FORMAT_ERROR'
        self.info = info

    def __str__(self):
        return repr('Format is error!({})'.format(self.info))


# 令牌无效
class TokenInvalid(CustomError):
    def __init__(self, info):
        self.return_code = 'TOKEN_INVALID'
        self.info = info

    def __str__(self):
        return repr(self.info)


# 权鉴无效
class AuthorizationInvalid(CustomError):
    def __init__(self, info):
        self.return_code = 'AUTHORIZATION_INVALID'
        self.info = info

    def __str__(self):
        return repr(self.info)

