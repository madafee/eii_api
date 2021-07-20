# -*- coding: utf-8 -*-

import collections
import functools
import inspect
import flask
from flask_restful import reqparse
from sqlalchemy.exc import IntegrityError, DataError
from werkzeug.exceptions import BadRequest, NotFound
from itsdangerous import BadSignature, SignatureExpired
from project import APP
from project.database import models
from project.common import response
from project.common import exception as ex
from project.common import request

__author__ = "liuxu"
# 装饰器


# 参数类型检查装饰器(支持检查*args, **kwargs参数)
def typeassert(*ty_args, **ty_kwargs):
    def decorate(func):
        # If in optimized mode, disable type checking
        if APP.config['MODE'] != 'develop':
            return func

        # Map function argument names to supplied types
        sig = inspect.signature(func)
        bound_types = sig.bind_partial(*ty_args, **ty_kwargs).arguments

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs)
            # Enforce type assertions across supplied arguments
            for name, value in bound_values.arguments.items():
                if name in bound_types:
                    if isinstance(value, (tuple, list)):
                        for i, subvalue in enumerate(value):
                            if not isinstance(subvalue, bound_types[name][i]):
                                raise TypeError('argument {}({}) must be {}'
                                                .format(name,
                                                        type(value),
                                                        bound_types[name]))
                    elif isinstance(value, dict):
                        for key, subvalue in value.items():
                            bound_type = bound_types[name].get(key)
                            if not bound_type or not isinstance(subvalue, bound_type):
                                raise TypeError('argument {}({}) must be {}'
                                                .format(name,
                                                        type(value),
                                                        bound_types[name]))
                    elif not isinstance(value, bound_types[name]):
                        raise TypeError('argument {}({}) must be {}'
                                        .format(name,
                                                type(value),
                                                bound_types[name]))
            return func(*args, **kwargs)
        return wrapper
    return decorate


# 给装饰器附加函数的装饰器
def attach_wrapper(obj, func=None):
    if func is None:
        return functools.partial(attach_wrapper, obj)
    setattr(obj, func.__name__, func)
    return func


# 通用log装饰器
def common_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        APP.log.info("\n{} {}".format(flask.request.method, flask.request.url))
        if flask.request.method in ('POST', 'PUT', 'DELETE'):
            APP.log.info("DATA: {}\n".format(
                flask.request.data.decode('utf-8') if flask.request.data else "NONE"))

        return func(*args, **kwargs)
    return wrapper


# 鉴权装饰器
def check_auth(*auth_list):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 导出Excel不鉴权
            if kwargs.get('is_xlsx'):
                return func(*args, **kwargs)

            auth_parse = reqparse.RequestParser()
            auth_parse.add_argument('Authorization', location='headers')
            authorization = auth_parse.parse_args()["Authorization"]

            if authorization:
                try:
                    auth_info = APP.authorization.verify(authorization)
                except Exception:
                    raise ex.AuthorizationInvalid('权鉴无效或已过期')

                user = models.TblUser.query.filter_by(id=auth_info['id']).first()
                if not user:
                    raise ex.TokenInvalid('无效的用户')
                else:
                    APP.log.info('USER: {}({})'.format(user.id, user.name))
                    # 验证权限
                    if not auth_list:
                        kwargs['user'] = user
                        flask.request.user_id = user.id
                        return func(*args, **kwargs)
                    else:
                        for auth in user.auths:
                            if auth in auth_list:
                                kwargs['user'] = user
                                flask.request.user_id = user.id
                                return func(*args, **kwargs)
                        else:
                            raise ex.ReturnError('USER_UNAUTHORIZED')
            else:
                raise ex.ReturnError('AUTHORIZATION_NOT_FOUND')

        @attach_wrapper(wrapper)
        def set_auth(*new_auth_list):
            nonlocal auth_list
            auth_list = new_auth_list

        return wrapper
    return decorator


# 通用异常处理装饰器
def check_except(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        is_commit = False
        try:
            ret = func(*args, **kwargs)
            models.DB.session.commit()
            is_commit = True
            return ret
        except BadRequest as inst:
            raise
        except NotFound as inst:
            return response.get_code('NOT_FOUND', info=inst)
        except IntegrityError as inst:
            return response.get_code('INTEGRITY_ERROR', info=inst)
        except TypeError as inst:
            return response.get_code('TYPE_ERROR', inst, info=inst)
        except DataError as inst:
            return response.get_code('DATA_ERROR', info=inst)
        except ValueError as inst:
            return response.get_code('VALUE_ERROR', inst, info=inst)
        except (BadSignature, SignatureExpired) as inst:
            return response.get_code('SIGNATURE_ERROR', inst, info=inst)
        except ex.CustomError as inst:
            return response.get_code(inst.return_code, inst, info=inst)
        except Exception as inst:
            return response.get_code('UNKNOWN_ERROR', info=inst)
        finally:
            if not is_commit:
                models.DB.session.rollback()
    return wrapper


# 取得分页信息装饰器
def get_page(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        page_parse = reqparse.RequestParser()
        page_parse.add_argument('page_size', required=True, nullable=False,
                                location='args', type=request.Type.positive)
        page_parse.add_argument('page_no', required=True, nullable=False,
                                location='args', type=request.Type.positive)

        page = page_parse.parse_args()
        kwargs['page'] = (page['page_no'], page['page_size'])

        return func(*args, **kwargs)
    return wrapper


# 取得query参数装饰器
def query_params(*query_list):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if query_list:
                query_parse = reqparse.RequestParser()
                for query in query_list:
                    query_parse.add_argument(query, location='args')
                query_args = query_parse.parse_args()

                for query in query_list:
                    kwargs[query] = query_args[query]

            return func(*args, **kwargs)

        @attach_wrapper(wrapper)
        def set_query(*new_query_list):
            nonlocal query_list
            query_list = new_query_list

        return wrapper
    return decorator


# api返回值排序
def sorted_return(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        if isinstance(ret.get('data'), list):
            for i, item in enumerate(ret['data']):
                sort_dict = collections.OrderedDict()
                for key, value in sorted(item.items(), key=lambda d: d[0]):
                    sort_dict[key] = value
                ret['data'][i] = sort_dict
        return ret
    return wrapper
