# -*- coding: utf-8 -*-

from sqlalchemy import func
from project import APP
from project.common import resource
from project.common import request
from project.common import response
from project.common import decorator
from project.common import common
from project.common import qcc
from project.common import datadictionary as dd
from project.common import exception as ex
from project.database.models import TblUser

__author__ = 'liuxu'
# 用户管理


@APP.api.resource('/users')
class Users(resource.Resource):
    req = request.RequestParser()
    # 登陆名
    req.add_body('login')
    # 密码
    req.add_body('password')
    # 角色
    req.add_body('role_id', choices=dd.Role.keys())
    # 姓名
    req.add_body('name')
    # 性
    req.add_body('gender', choices=[0, 1, 2])
    # 手机
    req.add_body('mobile')
    # 科室
    req.add_body('department')
    # 职位
    req.add_body('position')

    def __init__(self):
        super(Users, self).__init__()

    # 取得用户列表
    @decorator.check_auth(dd.Auth.MS)
    @decorator.get_page
    @decorator.query_params('keyword')  # 检索关键字，用户姓名
    def get(self, **kwargs):
        query = TblUser.query
        if kwargs['keyword']:
            query = query.filter((TblUser.name.contains(kwargs['keyword'])))

        users = (
            query
            .filter(TblUser.id != 1)
            .order_by(TblUser.id.desc())
            .paginate(*kwargs['page']))

        return response.get_value(users, response.Fields.USERS)

    # 新增用户信息
    @decorator.check_auth(dd.Auth.MS)
    def post(self, **kwargs):
        req_args = self.req.parse_args()

        TblUser.create(**req_args)

        return response.get_code('OK')


@APP.api.resource('/users/<int:id>')
class User(resource.Resource):
    req = request.RequestParser()
    # 密码
    req.add_body('password')
    # 角色
    req.add_body('role_id', choices=dd.Role.keys())
    # 有效性
    req.add_body('is_valid', choices=[0, 1])
    # 姓名
    req.add_body('name')
    # 性别
    req.add_body('gender', choices=[0, 1, 2])
    # 手机
    req.add_body('mobile')
    # 科室
    req.add_body('department')
    # 职位
    req.add_body('position')

    def __init__(self):
        super(User, self).__init__()

    # 取得用户信息
    @decorator.check_auth()
    def get(self, id, **kwargs):
        user = TblUser.get(id)

        return response.get_value(user, response.Fields.USERS)

    # 修改用户信息
    @decorator.check_auth(dd.Auth.MS)
    def put(self, id, **kwargs):
        req_args = self.req.parse_args()

        user = TblUser.get(id)
        user.update(**req_args)

        return response.get_code('OK')


@APP.api.resource('/users/user/authorization')
class UserAuthorization(resource.Resource):
    req = request.RequestParser()
    req.add_argument('token', location='headers')

    def __init__(self):
        super(UserAuthorization, self).__init__()

    # 换取令牌
    def get(self):
        req_args = self.req.parse_args()

        authorization = TblUser.verify_token(req_args['token'])

        ret = response.get_code('OK')
        ret['authorization'] = authorization

        return ret


@APP.api.resource('/users/user/login')
class UserLogin(resource.Resource):
    req = request.RequestParser()
    # 登陆名
    req.add_body('login')
    # 密码
    req.add_body('password')

    def __init__(self):
        super(UserLogin, self).__init__()

    # 用户登陆
    def post(self, **kwargs):
        req_args = self.req.parse_args()
        login = req_args['login']
        password = req_args['password']

        user = TblUser.query.filter_by(login=login).first()
        if not user or not user.verify_password(password):
            raise ex.ReturnError('USER_LOGIN_ERROR')

        ret = response.get_value(user, response.Fields.USERS)
        ret['authorization'] = user.generate_auth()
        ret['token'] = user.generate_token()

        return ret
