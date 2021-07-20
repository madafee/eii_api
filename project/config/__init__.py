# -*- coding: utf-8 -*-

__author__ = "liuxu"

import os
from project.common import serial

SECRET_KEYS = []
ENV_KEYS = ['MODE', 'SECRET', 'QCC_KEY', 'QCC_SECRET', 'QCC_LIMIT', 'QCC_TOKEN_HOST', 'SQLALCHEMY_DATABASE_URI']


def load_secret(mode, app, keys):
    serializer = serial.Serial()
    data = serializer.verify(app.config['SECRET'].encode())
    if data is None:
        msg = 'The secret key is invalid!'
        print(msg)
        raise

    for key in keys:
        app.config[key] = data[key]


def load_config(app):
    for key in ENV_KEYS:
        app.config[key] = os.environ.get(key)

    app.config.from_object(CommonConfig)
    if app.config['MODE'] == "develop":
        app.config.from_object(DevelopConfig)
    else:
        app.config.from_object(ProductConfig)

    load_secret(app.config['MODE'], app, SECRET_KEYS)


# 开发环境配置
class DevelopConfig(object):
    # log
    LOG_LEVEL = 10
    '''
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0
    '''
    DSN = "http://bd144ca1916349439ede4934a7289ccf@www.dlyunzhi.cn:7883/2"

    # 权鉴
    TOKEN_EXPIRED = 60000000
    AUTH_EXPIRED = 30000000

    # SQLAlchemy
    SQLALCHEMY_ECHO = False

    # Doclever
    DOCLEVER_HOST = 'http://192.168.1.13'
    DOCLEVER_LOGIN = 'liuxu'
    DOCLEVER_PASSWORD = 'abcd1234'
    PROJECT_NAME = 'EII'


# 生产环境配置
class ProductConfig(object):
    # log
    LOG_FILEPATH = "/opt/log/app.log"
    LOG_MAXBYTES = 20*1024*1024
    LOG_BACKUPCOUNT = 20
    LOG_CONTENT_FORMAT = "%(levelname)s[%(asctime)s]:%(message)s"
    LOG_DATA_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOG_LEVEL = 20
    '''
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0
    '''
    # DSN = "http://2805da2505bd49f0b3932c872cdf0558:0871cb2adc7143168004b3fe99e0f563@sentry.dlyunzhi.com/4"

    # 权鉴
    TOKEN_EXPIRED = 2592000
    AUTH_EXPIRED = 2592000


# 通用设置
class CommonConfig(object):
    # DB
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 定时任务
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
