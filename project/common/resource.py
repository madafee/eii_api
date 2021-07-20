# -*- coding: utf-8 -*-

from flask_restful import Resource
from project.common import decorator

__author__ = "liuxu"


# 自定义资源类
class Resource(Resource):
    # 资源方法全局装饰器
    method_decorators = [decorator.common_log, decorator.check_except]
