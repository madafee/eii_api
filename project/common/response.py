# -*- coding: utf-8 -*-

from flask_restful import fields, marshal
from flask_sqlalchemy import model, Pagination
from flask import request
from project import APP

RETURN_CODE = {
    'OK':                                   '正确',
    'UNKNOWN_ERROR':                        '未知错误',
    'BAD_REQUEST':                          '传入参数错误',
    'NOT_FOUND':                            '页面不存在',
    'INTEGRITY_ERROR':                      '该条数据已存在或数据关联关系不正确',
    'DATA_ERROR':                           '数据库数据错误',
    'TYPE_ERROR':                           '数据类型不正确',
    'VALUE_ERROR':                          '错误的数值',
    'SIGNATURE_ERROR':                      '签名无效或已过期',
    'LONG_POLL_TIMEOUT':                    '长轮询超时',

    'WECHAT_API_ERROR':                     '调用微信接口错误',
    'WECHAT_CODE_ERROR':                    '错误的用户CODE',
    'WECHAT_LOGIN_ERROR':                   '微信登陆失败',
    'WECHAT_USER_NOT_EXIST':                '微信用户不存在',

    'FORMAT_ERROR':                         '数据格式不正确',
    'RECORD_NOT_FOUND':                     '记录不存在',
    'DICTIONARY_NOT_FOUND':                 '字典不存在',
    'MODIFY_RECORD_ERROR':                  '记录不能被修改',
    'AUTHORIZATION_INVALID':                '无效的权鉴',
    'TOKEN_INVALID':                        '无效的令牌',

    'USER_UNAUTHORIZED':                    '没有权限或权限不足',
    'USER_INVALID':                         '无效的用户',
    'USER_LOGIN_ERROR':                     '用户登陆失败',
    'AUTHORIZATION_NOT_FOUND':              '未提供权鉴',
    'USER_ROLE_ERROR':                      '用户角色错误',
    'USER_EXISTED':                         '用户已存在',

    'WECHAT_API_ERROR':                     '调用微信接口错误',
    'WECHAT_CODE_ERROR':                    '错误的用户CODE',
    'WECHAT_LOGIN_ERROR':                   '微信登陆失败',
    'WECHAT_USER_NOT_EXIST':                '微信用户不存在',

    'SCHEDULER_EXISTED':                    '该时间段预约已存在',
    'RESERVED_MEETING_EXISTED':             '用户已有其它预约',
    'MEETING_CANNOT_APPOINT':               '该会议不能被预约',
    'MEETING_CANNOT_CANCEL':                '该会议预约不能被取消',

    'FIELD_EMPTY':                          '字段不能为空',
    'COMPANY_LIMIT':                        '重点监控公司数量超过限制',

}


class Datetime(fields.Raw):
    def format(self, value):
        return value.strftime('%Y-%m-%d %T')


class Date(fields.Raw):
    def format(self, value):
        return value.strftime('%Y-%m-%d')


class Fields(object):
    # return value define

    DICTIONARYS = {
        # 字典名
        'name': fields.String,
        # 字典内容
        'dict': fields.List(fields.Nested({
            # 编号
            'id': fields.Raw,
            # 名称
            'value': fields.String,
            # 子内容
            'sub_value': fields.List(fields.String),
            }))
    }

    USERS = {
        # 用户ID
        'id': fields.Integer,
        # 登陆名
        'login': fields.String,
        # 角色ID
        'role_id': fields.Integer,
        # 角色
        'role': fields.String,
        # 有效
        'is_valid': fields.Integer,
        # 姓名
        'name': fields.String,
        # 性别
        'gender': fields.String,
        # 手机
        'mobile': fields.String,
        # 科室
        'department': fields.String,
        # 职位
        'position': fields.String,
        # 有效
        'is_valid': fields.Integer,
        # 权限
        'auths': fields.List(fields.Integer),
    }

    ANNOUNCEMENTS = {
        # 名称
        'name': fields.String,
        # 申请日期
        'filed_date': fields.String,
        # 报告日期
        'report_date': fields.String,
        # 来源
        'source': fields.String,
        # 地址
        'location': fields.String,
        # 文件
        'file': fields.String,
    }

    ORDERS = {
        # ID
        'id': fields.Integer,
        # 发起者用户ID
        'initiator_id': fields.Integer,
        # 用户姓名
        'initiator': fields.String,
        # 地区ID
        'area_id': fields.Integer,
        # 地区
        'area': fields.String,
        # 状态ID
        'status_id': fields.Integer,
        # 状态
        'status': fields.String,
        # 内容
        'content': fields.String,
        # 创建日期
        'create_datetime': Date,
        # 更新日期
        'update_datetime': Date,
    }

    ORDER = {
        # ID
        'id': fields.Integer,
        # 发起者用户ID
        'initiator_id': fields.Integer,
        # 用户姓名
        'initiator': fields.String,
        # 地区ID
        'area_id': fields.Integer,
        # 地区
        'area': fields.String,
        # 状态ID
        'status_id': fields.Integer,
        # 状态
        'status': fields.String,
        # 内容
        'content': fields.String,
        # 创建日期
        'create_datetime': Date,
        # 更新日期
        'update_datetime': Date,
        # 记录
        'records': fields.List(fields.Nested({
            # 用户姓名
            'user': fields.String,
            # 内容
            'content': fields.String,
            # 类型ID
            'type_id': fields.Integer,
            # 类型
            'type': fields.String,
            # 创建日期
            'create_datetime': Date,
            }))
    }

    ORDER_STATISTIC = {
        # 地区工单
        'area_data': fields.List(fields.Nested({
            # 名称
            'name': fields.String,
            # 数量
            'count': fields.Integer,
            })),
        # 状态工单
        'status_data': fields.List(fields.Nested({
            # 名称
            'name': fields.String,
            # 数量
            'count': fields.Integer,
            }))
    }

    COMPANYS = {
        # ID
        'id': fields.Integer,
        # 内部KeyNo
        'keyno': fields.String,
        # 公司名称
        'name': fields.String,
        # 法人名称
        'opername': fields.String,
        # 成立日期
        'startdate': fields.String,
        # 企业状态
        'status': fields.String,
        # 注册号
        'no': fields.String,
        # 统一社会信用代码
        'creditcode': fields.String,
    }

    COMPANY = {
        # 内部KeyNo
        'keyno': fields.String,
        # 公司名称
        'name': fields.String,
        # 注册号
        'no': fields.String,
        # 登记机关
        'belongorg': fields.String,
        # 法人ID
        'operid': fields.String,
        # 法人名
        'opername': fields.String,
        # 成立日期
        'startdate': fields.String,
        # 吊销日期
        'enddate': fields.String,
        # 企业状态
        'status': fields.String,
        # 省份
        'province': fields.String,
        # 更新日期
        'updateddate': fields.String,
        # 统一社会信用代码
        'creditcode': fields.String,
        # 注册资本
        'registcapi': fields.String,
        # 企业类型
        'econkind': fields.String,
        # 地址
        'address': fields.String,
        # 经营范围
        'scope': fields.String,
        # 营业开始日期
        'termstart': fields.String,
        # 营业结束日期
        'teamend': fields.String,
        # 发照日期
        'checkdate': fields.String,
        # 组织机构代码
        'orgno': fields.String,
        # 是否上市(0为未上市，1为上市)
        'isonstock': fields.String,
        # 上市公司代码
        'stocknumber': fields.String,
        # 上市类型
        'stocktype': fields.String,
        # 企业类型，
        'enttype': fields.String,
        # 实缴资本
        'reccap': fields.String,
        # 股权信息
        'stocklist': fields.Nested({
            # 实体点
            'points': fields.List(fields.Nested({
                # 名称
                'name': fields.String,
                # 大小
                'percent': fields.String,
                })),
            # 关系
            'connects': fields.List(fields.Nested({
                # 起点
                'source': fields.String,
                # 终点
                'dest': fields.String,
                # 值
                'value': fields.String,
                })),
        }),
        # 股东信息
        'partners': fields.List(fields.Nested({
            # 投资人姓名
            'stockname': fields.String,
            # 投资人类型
            'stocktype': fields.String,
            # 出资比例
            'stockpercent': fields.String,
            # 认缴出资额
            'shouldcapi': fields.String,
            # 认缴出资时间
            'shouddate': fields.String,
        })),
        # 股权变更信息
        'stockchanges': fields.List(fields.Nested({
            # 旧股权信息
            'old_stocklist': fields.Nested({
                # 实体点
                'points': fields.List(fields.Nested({
                    # 名称
                    'name': fields.String,
                    # 大小
                    'percent': fields.String,
                    })),
                # 关系
                'connects': fields.List(fields.Nested({
                    # 起点
                    'source': fields.String,
                    # 终点
                    'dest': fields.String,
                    # 值
                    'value': fields.String,
                })),
            }),
            # 新股权信息
            'new_stocklist': fields.Nested({
                # 实体点
                'points': fields.List(fields.Nested({
                    # 名称
                    'name': fields.String,
                    # 大小
                    'percent': fields.String,
                    })),
                # 关系
                'connects': fields.List(fields.Nested({
                    # 起点
                    'source': fields.String,
                    # 终点
                    'dest': fields.String,
                    # 值
                    'value': fields.String,
                })),
            }),
            # 变更信息
            'change_info': fields.List(fields.String),
            # 变更时间
            'create_datetime': Datetime,
        })),
        # 是否检查变更
        'is_track': fields.String,
    }

    STOCKCHANGES = {
        # 企业ID
        'company_id': fields.Integer,
        # 企业名称
        'company_name': fields.String(attribute='company.name'),
        # 变更信息
        'change_info': fields.List(fields.String),
        # 变更时间
        'create_datetime': Datetime,
    }


def get_code(key, extra=None, *, info=None):
    msg = RETURN_CODE.get(key)
    if msg is None:
        raise ValueError('invalid return code: {key}'.format(key=key))

    if str(extra) and extra:
        msg = '{}({})'.format(msg, extra)

    if key not in ('OK'):
        debug_log(key, msg, info)

    return {'code': key, 'msg': msg}


def get_value(value, field, *, count=None):
    if isinstance(value, Pagination):
        # 分页数据（类型：Pagination类）
        count = value.total
        data = value.items
    elif isinstance(value, (list, tuple)):
        # 多条数据
        count = count or len(value)
        data = value
    elif isinstance(value, (model.Model, dict, type)):
        # 单条数据（不分页）
        count = 1
        data = [value]
    else:
        raise ValueError('return value type error')

    # 包装返回值
    wrap_values = get_code('OK')
    wrap_values['data'] = data
    wrap_values['count'] = count

    # 包装返回格式
    wrap_fields = {'code': fields.String}
    wrap_fields['msg'] = fields.String
    wrap_fields['count'] = fields.Integer
    wrap_fields['data'] = fields.List(fields.Nested(field))

    return marshal(wrap_values, wrap_fields)


# 打印调试信息
def debug_log(key, msg, info="None"):
    data = (request.data.decode('utf-8')
            if request.data else "NO REQUEST DATA!")

    msg = "--------------- ERROR DEBUG INFO ---------------\n"\
        "{method} {url}\n"\
        "HEADERS: \n{header}"\
        "DATA: {data}\n"\
        "ERROR: {key}({msg})\n"\
        "EXTRA: {info}\n"\
        "--------------------------------------------------\n"\
        .format(method=request.method,
                url=request.url,
                header=request.headers,
                data=data,
                key=key,
                msg=msg,
                info=info)

    APP.log.exception(msg)
