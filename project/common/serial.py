# -*- coding: utf-8 -*-

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

__author__ = "liuxu"


class Serial(object):
    """ 加密字符串 """
    def __init__(self, *, secret_key='dlyunzhi', salt='tech', expires_in=None):
        self._serializer = Serializer(
            secret_key,
            salt=salt,
            expires_in=expires_in,
            algorithm_name='HS256')
        super(Serial, self).__init__()

    def generate(self, data):
        return self._serializer.dumps(data).decode()

    def verify(self, serial):
        return self._serializer.loads(serial)
