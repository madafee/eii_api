# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all()
import os
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler as FileHandler
from flask_cors import CORS
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from flask import Flask
from flask_apscheduler import APScheduler
from flask_restful import Api
from flask_doclever import flask_doclever
from project import config
from project.common import serial

APP = Flask(__name__)


def init_app():
    # debug模式下, 仅在子进程时执行初始化
    if os.environ.get('MODE') == 'develop' and not os.environ.get('WERKZEUG_RUN_MAIN'):
        return APP

    flask_restful_errors = {
        'BadRequest': {
            'code': 'BAD_REQUEST',
            'msg': '传入参数错误',
            'status': 200,
        },
    }

    APP.api = Api(APP, errors=flask_restful_errors)

    # CORS
    CORS(APP)

    # load config
    config.load_config(APP)

    # jwt init
    init_serial()

    # log init
    init_logger()

    # doclever init
    if os.environ.get('MODE') == 'develop':
        from project.common import response
        flask_doclever.init(APP, response.Fields)

    # db init
    init_db()

    # 定时任务
    init_apscheduler()

    # route init
    init_route()

    print("API IS RUNNING!")

    return APP


def init_route():
    MODULE_EXTENSIONS = ('.py', '.pyc', '.pyo', '.pye')
    pkgpath = Path.joinpath(Path(__file__).parent, 'resources')

    def import_path(path):
        parts = path.parts[path.parts.index('resources')::]
        root = 'project.{}'.format('.'.join(parts))

        for file in path.iterdir():
            if file.is_file():
                if file.suffix in MODULE_EXTENSIONS:
                    __import__('{}.{}'.format(root, file.stem))
            else:
                if file.stem == '__pycache__':
                    continue
                import_path(file)

    import_path(pkgpath)


# init logger
def init_logger():
    # 配置LOG
    logger = logging.getLogger('LOG')
    logger.setLevel(APP.config['LOG_LEVEL'])

    if APP.config['MODE'] == 'develop':
        # 输出到屏幕
        consolelog = logging.StreamHandler()
        consolelog.setLevel(APP.config['LOG_LEVEL'])
        logger.addHandler(consolelog)

    else:
        # 输出到文件
        # RotatingFileHandler = logging.handlers.RotatingFileHandler
        filelog = FileHandler(APP.config['LOG_FILEPATH'],
                              maxBytes=APP.config['LOG_MAXBYTES'],
                              backupCount=APP.config['LOG_BACKUPCOUNT'],
                              encoding="UTF-8")
        filelog.setFormatter(
            logging.Formatter(APP.config['LOG_CONTENT_FORMAT'],
                              datefmt=APP.config['LOG_DATA_FORMAT']))
        logger.addHandler(filelog)

    # 输出到sentry
    if APP.config.get('DSN', None):
        sentry_sdk.init(dsn=APP.config['DSN'], integrations=[FlaskIntegration()])

    APP.log = logger


def init_serial():
    APP.authorization = serial.Serial(expires_in=APP.config['AUTH_EXPIRED'])
    APP.token = serial.Serial(salt='dl', expires_in=APP.config['TOKEN_EXPIRED'])


def init_db():
    from project.database import models
    from sqlalchemy.ext.declarative import declarative_base

    # 创建指的表
    tables = []
    ignore_tables = []

    for model in models.DB.metadata.tables.values():
        if hasattr(model, 'name') and model.name not in ignore_tables:
            tables.append(model)

    Base = declarative_base(metadata=models.DB.metadata)
    Base.metadata.create_all(models.DB.engine, tables=tables)
    # 初始化表数据
    models.init_database()


def init_apscheduler():
    scheduler = APScheduler()
    scheduler.init_app(APP)
    scheduler.start()

    APP.scheduler = scheduler
