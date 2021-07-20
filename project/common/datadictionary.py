# -*- coding: utf-8 -*-

import collections
from project import APP
from project.common import response
from project.common import resource
from project.common import exception as ex


__author__ = "liuxu"
# 数据字典（data dictionary）


Item = collections.namedtuple('Item', ['key', 'value', 'sub_value'])
Item.__new__.__defaults__ = (0, '', None)


@APP.api.resource('/dicts/<string:name>')
class Dictionary(resource.Resource):
    def __init__(self):
        super(Dictionary, self).__init__()

    # 取得字典信息
    def get(self, name, **kwargs):
        if name == 'all':
            dicts = DataDictionary.get_all_dd()
        else:
            dicts = DataDictionary.get_dd(name)
            if not dicts:
                raise ex.ReturnError('DICTIONARY_NOT_FOUND')

            dicts = [dicts]

        return response.get_value(dicts, response.Fields.DICTIONARYS)


class DataDictionaryMeta(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if cls.__name__.lower() != 'datadictionary':
            cls._cls_name[cls.__name__.lower()] = cls
            setattr(cls, '_items', {})
            setattr(cls, '_sub_items', {})
            setattr(cls, '_item_name', {})
            for obj_name in dir(cls):
                if obj_name[0] != '_':
                    item = getattr(cls, obj_name)
                    if isinstance(item, tuple):
                        cls._items[item.key] = item.value
                        cls._sub_items[item.key] = item.sub_value or []
                        cls._item_name[item.key] = obj_name
                        setattr(cls, obj_name, item.key)


class DataDictionary(metaclass=DataDictionaryMeta):
    __abstract__ = True

    # ex. {'role': Role, 'costtype': CostType}
    _cls_name = collections.OrderedDict()

    # ex. {1: '管理', 2: '清洗'}
    _items = collections.OrderedDict()
    # ex. {1: ['管理1', '管理1'], 2: ['清洗1', '清洗2']}
    _sub_items = collections.OrderedDict()
    # {1:'ITEM1_NAME', 2: 'ITEM2_NAME'}
    _item_name = collections.OrderedDict()

    @classmethod
    def get_dd(cls, name):
        dd = cls._cls_name.get(name.lower())
        if dd:
            return {'name': name, 'dict': dd.gets()}

    @classmethod
    def get_all_dd(cls):
        return [{'name': name, 'dict': dd.gets()} for name, dd in cls._cls_name.items()]

    @classmethod
    def get(cls, id, default=None):
        return cls._items.get(id, default)

    @classmethod
    def get_sub(cls, id):
        return cls._sub_items.get(id)

    @classmethod
    def search(cls, value):
        for k, v in cls._items.items():
            if v == value:
                return {'id': k, 'value': v}

    @classmethod
    def keys(cls):
        return cls._items.keys()

    @classmethod
    def names(cls):
        return cls._item_name

    @classmethod
    def gets(cls):
        return [{'id': key, 'value': value, 'sub_value': cls._sub_items.get(key)}
                for key, value in cls._items.items()]


# 权限
class Auth(DataDictionary):
    MS = Item(1, '管理')
    IQ = Item(2, '查询')
    AS = Item(3, '回答')


# 角色
class Role(DataDictionary):
    SUPER = Item(1, '超级管理员', [1, 2, 3])
    MANAGER = Item(2, '管理员', [1, 2])
    CLIENT = Item(3, '用户', [2])


# 定单状态
class OrderStatus(DataDictionary):
    SUBMIT = Item(1, '已提交')
    PROCESSING = Item(2, '处理中')
    REPLY = Item(3, '已回复')
    COMPLETED = Item(4, '已解决')


# 地区
class Area(DataDictionary):
    MG = Item(1, '美国')
    XG = Item(2, '香港')
    RB = Item(3, '日本')
    WJQD = Item(4, '维京群岛')
    KMQD = Item(5, '开曼群岛')
    XJP = Item(6, '新加坡')
    BD = Item(7, '冰岛')


# 公告类型
class AnnouncementType(DataDictionary):
    A1 = Item('DEF 14A', '股东大会文件')
    A2 = Item('PRE 14C', '股东大会前披露')
    A3 = Item('DEF 14C', '股东大会最终文件')
    A4 = Item('10-K', '招股书')
    A5 = Item('F-1', '外国公司招股书')
    A6 = Item('10-K', '年报')
    A7 = Item('10-Q', '季报')
    A8 = Item('8-K', '重大事件')
    A9 = Item('4', '内部交易报告')
    A10 = Item('20-F', '外国公司年报')
    A11 = Item('3', '初始内部人持股报告')
    A12 = Item('6-K', '当期报告')
    A13 = Item('SC 13D/A', '实益所有权报告')
    A14 = Item('SC 13E3/A', '私人交易')
    A15 = Item('S-3/A', '注册声明')
    A16 = Item('NPORT-P', '非必要报告')
    A17 = Item('8-K/A', '重大事件')
    A18 = Item('S-4/A', '并购交易')
    A19 = Item('F-1/A', '外国公司注册')
    A20 = Item('10-K/A', '招股书')


# 类型
class RecordType(DataDictionary):
    Q = Item(1, '问题')
    A = Item(2, '回答')


# 公司类型
class EnterpriseType(DataDictionary):
    ET_1 = Item('0', '公司')
    ET_2 = Item('1', '社会组织')
    ET_3 = Item('3', '香港公司')
    ET_4 = Item('4', '政府机构')
    ET_5 = Item('5', '台湾公司')
    ET_6 = Item('6', '基金会')
    ET_7 = Item('7', '医院')
    ET_8 = Item('8', '海外公司')
    ET_9 = Item('9', '律师事务所')
    ET_10 = Item('10', '学校')
    ET_11 = Item('-1', '其他')

