# -*- coding: utf-8 -*-

import datetime
from itertools import groupby
from passlib.apps import custom_app_context as pwd_context
import sqlalchemy
from project import APP
from project.common import utils
from project.common import exception as ex
from project.common import datadictionary as dd
from project.database import modelbase
from project.database import descriptor

__author__ = "liuxu"

DB = modelbase.DB
ReferenceColumn = modelbase.ReferenceColumn


# 用户信息
class TblUser(modelbase.Model):
    __tablename__ = 'user'

    # 登陆名
    login = DB.Column(DB.String(32), unique=True, nullable=False)
    password_hash = DB.Column(DB.String(128), nullable=False)
    # 角色
    role_id = DB.Column(DB.Integer, nullable=False)
    role = descriptor.DataDictionary('role_id', dd.Role)
    # 姓名
    name = DB.Column(DB.String(128), nullable=False)
    # 性别
    gender = DB.Column(DB.Integer, default=0)
    # 手机
    mobile = DB.Column(DB.String(16))
    # 科室
    department = DB.Column(DB.String(16))
    # 职位
    position = DB.Column(DB.String(64))
    # 有效
    is_valid = DB.Column(DB.Integer, default=1)
    # 交换令牌
    token = DB.Column(DB.String(128))

    @property
    def auths(self):
        return dd.Role.get_sub(self.role_id)

    @property
    def password(self):
        return None

    @password.setter
    def password(self, password):
        if password:
            self.password_hash = pwd_context.encrypt(password)

    def generate_auth(self):
        info = {'id': self.id, 'name': self.name, 'role_id': self.role_id}
        return APP.authorization.generate(info)

    def generate_token(self):
        return APP.token.generate({'id': self.id})

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    @classmethod
    def verify_token(cls, token_serial):
        try:
            token_info = APP.token.verify(token_serial)
        except Exception:
            raise ex.TokenInvalid('签名无效或已过期')

        user = cls.get(token_info['id'])

        return user.generate_auth()

    def __init__(self, login, password, role_id, name, gender, mobile,
                 department, position):
        self.login = login
        self.password = password
        self.role_id = role_id
        self.name = name
        self.gender = gender
        self.mobile = mobile
        self.department = department
        self.position = position


# 工单信息
class TblOrder (modelbase.Model):
    __tablename__ = 'order'

    # 发起者用户ID
    initiator_id = DB.Column(DB.Integer)
    # 用户姓名
    initiator = descriptor.User('initiator_id')
    # 地区ID
    area_id = DB.Column(DB.Integer)
    # 地区
    area = descriptor.DataDictionary('area_id', dd.Area)
    # 状态ID
    status_id = DB.Column(DB.Integer)
    # 状态
    status = descriptor.DataDictionary('status_id', dd.OrderStatus)
    # 内容
    content = DB.Column(DB.TEXT)
    # 记录
    records = DB.relationship('TblOrderRecord')

    def __init__(self, *, initiator_id, area_id, content):
        self.initiator_id = initiator_id
        self.area_id = area_id
        self.content = content
        self.status_id = dd.OrderStatus.SUBMIT


# 工单记录信息
class TblOrderRecord (modelbase.Model):
    __tablename__ = 'order_record'

    # 工单ID
    order_id = ReferenceColumn('order')
    # 用户ID
    user_id = DB.Column(DB.Integer)
    # 用户姓名
    user = descriptor.User('user_id')
    # 记录类型ID
    type_id = DB.Column(DB.Integer)
    # 记录类型
    type = descriptor.DataDictionary('type_id', dd.RecordType)
    # 内容
    content = DB.Column(DB.TEXT)

    def __init__(self, *, order_id, user_id, type_id, content):
        self.order_id = order_id
        self.user_id = user_id
        self.type_id = type_id
        self.content = content


# 企业信息
class TblCompany (modelbase.Model):
    __tablename__ = 'company'

    # 内部KeyNo
    keyno = DB.Column(DB.String(128))
    # 公司名称
    name = DB.Column(DB.String(128))
    # 注册号
    no = DB.Column(DB.String(128))
    # 登记机关
    belongorg = DB.Column(DB.String(128))
    # 法人ID
    operid = DB.Column(DB.String(128))
    # 法人名
    opername = DB.Column(DB.String(128))
    # 成立日期
    startdate = DB.Column(DB.String(128))
    # 吊销日期
    enddate = DB.Column(DB.String(128))
    # 企业状态
    status = DB.Column(DB.String(128))
    # 省份
    province = DB.Column(DB.String(128))
    # 更新日期
    updateddate = DB.Column(DB.String(128))
    # 统一社会信用代码
    creditcode = DB.Column(DB.String(128))
    # 注册资本
    registcapi = DB.Column(DB.String(128))
    # 企业类型
    econkind = DB.Column(DB.String(128))
    # 地址
    address = DB.Column(DB.String(128))
    # 经营范围
    scope = DB.Column(DB.Text)
    # 营业开始日期
    termstart = DB.Column(DB.String(128))
    # 营业结束日期
    teamend = DB.Column(DB.String(128))
    # 发照日期
    checkdate = DB.Column(DB.String(128))
    # 组织机构代码
    orgno = DB.Column(DB.String(128))
    # 是否上市(0为未上市，1为上市)
    isonstock = DB.Column(DB.String(128))
    # 上市公司代码
    stocknumber = DB.Column(DB.String(128))
    # 上市类型
    stocktype = DB.Column(DB.String(128))
    # 企业类型，
    enttype = DB.Column(DB.String(128))
    # 实缴资本
    reccap = DB.Column(DB.String(128))
    # 股东信息
    partners = DB.Column(DB.JSON, default={})
    # 股权信息
    stocklist = DB.Column(DB.JSON, default={})
    # 股权变更时间
    stock_datetime = DB.Column(DB.DateTime)
    # 股权变更记录
    stockchanges = DB.relationship('TblStockChange')
    # 是否检查变更
    is_track = DB.Column(DB.Integer, default=1)

    def __init__(self, *, keyno, name, no, belongorg, operid, opername, startdate,
                 enddate, status, province, updateddate, creditcode, registcapi,
                 econkind, address, scope, termstart, teamend, checkdate, orgno,
                 isonstock, stocknumber, stocktype, enttype, reccap, stocklist,
                 partners, is_track):
        self.keyno = keyno
        self.name = name
        self.no = no
        self.belongorg = belongorg
        self.operid = operid
        self.opername = opername
        self.startdate = startdate
        self.enddate = enddate
        self.status = status
        self.province = province
        self.updateddate = updateddate
        self.creditcode = creditcode
        self.registcapi = registcapi
        self.econkind = econkind
        self.address = address
        self.scope = scope
        self.termstart = termstart
        self.teamend = teamend
        self.checkdate = checkdate
        self.orgno = orgno
        self.isonstock = isonstock
        self.stocknumber = stocknumber
        self.stocktype = stocktype
        self.enttype = enttype
        self.reccap = reccap
        self.stocklist = stocklist
        self.stock_datetime = datetime.datetime.now()
        self.partners = partners
        self.is_track = is_track


# 股权变更信息
class TblStockChange (modelbase.Model):
    __tablename__ = 'stock_change'

    # 企业ID
    company_id = ReferenceColumn('company')
    # 企业信息
    company = DB.relationship('TblCompany', viewonly=True)
    # 旧股权信息
    old_stocklist = DB.Column(DB.JSON, default={})
    # 新股权信息
    new_stocklist = DB.Column(DB.JSON, default={})
    # 变更信息
    change_info = DB.Column(DB.JSON, default=[])

    def __init__(self, *, company_id, old_stocklist, new_stocklist, change_info):
        self.company_id = company_id
        self.old_stocklist = old_stocklist
        self.new_stocklist = new_stocklist
        self.change_info = change_info


def init_database():
    # 创建初始ROOT用户
    try:
        if TblUser.query.filter_by(id=1).count() == 0:
            DB.session.execute(
                (
                    "insert into user "
                    "(id, login, password_hash, role_id, name) "
                    "values "
                    "('1', 'root', '{password}', 1, '系统') "
                    .format(password=pwd_context.encrypt('abcd1234'))
                    ))

            DB.session.commit()
    except Exception as inst:
        APP.log.exception(inst)
        DB.session.rollback()
