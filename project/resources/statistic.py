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


@APP.api.resource('/orders/statistic')
class OrderStatistic(resource.Resource):
    def __init__(self):
        super(OrderStatistic, self).__init__()

    # 取得工单统计
    @decorator.check_auth()
    def get(self, **kwargs):
        op_user = kwargs['user']
        orders = TblOrder.query.filter_by(initiator_id=op_user.id).all()

        # 统计地区工单数
        area_data = {
            area['id']: {'name': area['value'], 'count': 0}
            for area in dd.Area.gets()
        }

        for order in orders:
            area = area_data.get(order.area_id)
            if area:
                area['count'] += 1

        # 统计状态工单数
        status_data = {
            status['id']: {'name': status['value'], 'count': 0}
            for status in dd.OrderStatus.gets()
        }

        for order in orders:
            status = status_data.get(order.status_id)
            if status:
                status['count'] += 1

        ret = {
            'area_data': list(area_data.values()),
            'status_data': list(status_data.values())}
        return response.get_value(ret, response.Fields.ORDER_STATISTIC)
