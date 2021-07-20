# -*- coding: utf-8 -*-

from sqlalchemy import func
from project import APP
from project.common import resource
from project.common import request
from project.common import response
from project.common import decorator
from project.common import common
from project.common import utils
from project.common import datadictionary as dd
from project.common import exception as ex
from project.database.models import TblOrder
from project.database.models import TblOrderRecord
from project.database.models import TblUser

__author__ = 'liuxu'
# 工单管理


@APP.api.resource('/orders')
class Orders(resource.Resource):
    req = request.RequestParser()
    # 地区ID
    req.add_body('area_id', type=int)
    # 内容
    req.add_body('content')

    def __init__(self):
        super(Orders, self).__init__()

    # 取得工单列表
    @decorator.check_auth()
    @decorator.get_page
    @decorator.query_params('status_id')  # 取得指定状态的工单
    def get(self, **kwargs):
        op_user = kwargs['user']
        status_id = kwargs['status_id']

        query = TblOrder.query
        if status_id:
            query = query.filter_by(status_id=status_id)

        if op_user.role_id != dd.Role.SUPER:
            query = query.filter_by(initiator_id=op_user.id)

        orders = query.order_by(TblOrder.id.desc()).paginate(*kwargs['page'])

        return response.get_value(orders, response.Fields.ORDERS)

    # 新增工单
    @decorator.check_auth()
    def post(self, **kwargs):
        op_user = kwargs['user']

        req_args = self.req.parse_args()

        TblOrder.create(initiator_id=op_user.id, **req_args)

        return response.get_code('OK')


@APP.api.resource('/orders/<int:id>')
class Order(resource.Resource):
    req = request.RequestParser()
    # 地区ID
    req.add_body('area_id', type=int)
    # 内容
    req.add_body('content')

    def __init__(self):
        super(Order, self).__init__()

    # 取得工单详情
    @decorator.check_auth()
    def get(self, id, **kwargs):
        order = TblOrder.get(id)

        return response.get_value(order, response.Fields.ORDER)


@APP.api.resource('/orders/<int:id>/status')
class OrderStatus(resource.Resource):
    req = request.RequestParser()
    # 状态ID
    req.add_body('status_id', type=dd.OrderStatus.keys())

    def __init__(self):
        super(OrderStatus, self).__init__()

    # 取得工单详情
    @decorator.check_auth()
    def put(self, id, **kwargs):
        req_args = self.req.parse_args()

        order = TblOrder.get(id)
        order.update(status_id=req_args['status_id'])

        return response.get_code('OK')


@APP.api.resource('/orders/<int:id>/records')
class OrderRecords(resource.Resource):
    req = request.RequestParser()
    # 内容
    req.add_body('content')

    def __init__(self):
        super(OrderRecords, self).__init__()

    # 新增记录
    @decorator.check_auth()
    def post(self, id, **kwargs):
        op_user = kwargs['user']

        req_args = self.req.parse_args()

        order = TblOrder.get(id)

        type_id = dd.RecordType.Q
        # 管理员回复，工单状态为已回复
        if op_user.role_id == dd.Role.SUPER:
            order.update(status_id=dd.OrderStatus.REPLY)
            type_id = dd.RecordType.A
        elif op_user.role_id in (dd.Role.MANAGER, dd.Role.CLIENT):
            order.update(status_id=dd.OrderStatus.PROCESSING)
            type_id = dd.RecordType.Q

        TblOrderRecord.create(
            user_id=op_user.id,
            order_id=order.id,
            type_id=type_id,
            **req_args)

        return response.get_code('OK')
