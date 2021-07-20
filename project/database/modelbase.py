# -*- coding: utf-8 -*-

import datetime
import binascii
import sqlalchemy
from sqlalchemy.orm.attributes import flag_modified
from flask_sqlalchemy import SQLAlchemy
from project import APP
from project.common import exception as ex

__author__ = "joshfriend"

# 数据库封装

DB = SQLAlchemy(APP)


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD operations.
    """
    id = DB.Column(DB.Integer, primary_key=True)
    create_datetime = DB.Column(DB.DateTime, default=datetime.datetime.now)
    update_datetime = DB.Column(DB.DateTime,
                                default=datetime.datetime.now,
                                onupdate=datetime.datetime.now)

    @classmethod
    def get(cls, id):
        if not id or id < 0:
            raise ex.NonRecordError('{}({})'.format(cls.__tablename__, id))
        data = cls.query.get(id)
        if not data:
            raise ex.NonRecordError('{}({})'.format(cls.__tablename__, id))
        return data

    @classmethod
    def gets(cls, *, page_no, page_size, filters=None, sorts=None):
        query = cls.query

        if filters:
            query = query.filter_by(**filters)

        if sorts:
            for order_by in sorts:
                column_name = order_by.get('desc', order_by.get('asc'))
                column = getattr(cls, column_name)

                if order_by.get('desc'):
                    query = query.order_by(sqlalchemy.desc(column))
                else:
                    query = query.order_by(sqlalchemy.asc(column))

        data = query.paginate(page_no, page_size)

        return data

    @classmethod
    def create(cls, commit=False, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save(commit)

    def update(self, commit=False, **kwargs):
        """Update specific fields of a record."""
        # Prevent changing ID of object
        kwargs.pop('id', None)
        for attr, value in kwargs.items():
            # 值为json(dict, list),并且是orm属性时，设置更新标识
            if isinstance(value, (dict, list)):
                cls_obj = getattr(self.__class__, attr)
                if isinstance(cls_obj, sqlalchemy.orm.attributes.InstrumentedAttribute):
                    flag_modified(self, attr)

            setattr(self, attr, value)

        return commit and self.save() or self

    def delete(self, commit=False):
        """Remove the record from the database."""
        DB.session.delete(self)
        return commit and DB.session.commit()

    def save(self, commit=False):
        """Save the record."""
        DB.session.add(self)
        if commit:
            DB.session.commit()
        else:
            DB.session.flush()
        return self


class Model(CRUDMixin, DB.Model):
    """Base model class that includes CRUD convenience methods."""
    __abstract__ = True


def ReferenceColumn(tablename, pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = ReferenceColumn('category')
        category = relationship('Category', backref='categories')
    """
    return DB.Column(DB.Integer,
                     DB.ForeignKey("{}.{}".format(tablename, pk_name)),
                     **kwargs)


# SQL FIELD
class Field(object):
    def __init__(self, name, value=None, *, type=None):
        # 字段名
        self.name = name
        # 类型
        self.type = type
        # 值
        if value is None:
            self.value = 'NULL'
        else:
            if type == 'UTF8':
                # UTF8转US7ASCII, 需要把值转为HEX格式传给oracle，在oracle中再转为US7ASCII
                raw = binascii.hexlify(value.encode('gbk')).decode().upper()
                self.value = 'UTL_RAW.CAST_TO_VARCHAR2(HEXTORAW(\'{}\'))'.format(raw)
            elif type == 'RAW':
                # UTF8转HEX
                self.value = binascii.hexlify(value.encode('gbk')).decode().upper()
            elif type == 'DATETIME':
                self.value = 'TO_DATE(\'{}\', \'YYYY-MM-DD HH24:MI:SS\')'.format(value)
            elif type == 'STRING':
                self.value = '\'{}\''.format(value)
            else:
                self.value = value

        super(Field, self).__init__()

    def __repr__(self):
        return self.value or ''

    def data(self, raw):
        try:
            if raw is None:
                return raw

            # 该字段查询到的值做格式转换
            if self.type == 'UTF8':
                string = ''.join(['%c' % c for c in binascii.unhexlify(raw)])
                string = string.encode('ISO-8859-1').decode('gbk')
                return string.encode('utf-8').decode('utf-8')
            elif self.type == 'STRING':
                return str(raw)
            elif self.type == 'INTEGER':
                return int(raw)
            elif self.type == 'FLOAT':
                return float(raw)
            else:
                return raw
        except Exception as inst:
            APP.log.exception(inst)
            if self.type == 'UTF8':
                return ""
            elif self.type == 'STRING':
                return ""
            elif self.type == 'INTEGER':
                return 0
            elif self.type == 'FLOAT':
                return 0.0
            else:
                return raw


class InsertFields(object):
    def __init__(self, *args):
        self._fields = args

    def __repr__(self):
        # 返回拼接的查询字段
        fields_name = [str(field.name) for field in self._fields]
        fields_value = [str(field.value) for field in self._fields]

        fields_string = (
            '({name}) values ({value})'
            .format(
                name=', '.join(fields_name),
                value=', '.join(fields_value)))

        return fields_string


class SelectFieldsMeta(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ex. 类{ret_name<属性名>, 'name<查询字段名>', 'type<类型>'}}
        setattr(cls, '_fields', [])

        for obj_name in dir(cls):
            if obj_name[0] != '_':
                item = getattr(cls, obj_name)
                if isinstance(item, Field):
                    item.ret_name = obj_name
                    cls._fields.append(item)

    def __repr__(cls):
        # 返回拼接的查询字段
        fields_value = []
        for field in cls._fields:
            if field.type == 'UTF8':
                # 当要查询的字符编码为US7ASCII, 需要把查询字段转为hex格式，得到的查
                # 询结果再用binascii.unhexlify转为UTF8
                fields_value.append(
                    'RAWTOHEX(UTL_RAW.CAST_TO_RAW({}))'.format(field.name))
            elif field.type == 'STRING_DATE':
                fields_value.append(
                    'TO_CHAR({}, \'YYYY-MM-DD\')'.format(field.name))
            else:
                fields_value.append(field.name)

        fields_string = ', '.join(fields_value)
        return fields_string


class SelectFields(metaclass=SelectFieldsMeta):
    _fields = []

    def __init__(self, *args):
        if len(args) != len(self._fields):
            raise TypeError('Expected {} arguments'.format(len(self._fields)))
        # 把查询结果值转为属性值
        for field, raw in zip(self._fields, args):
            setattr(self, field.ret_name, field.data(raw))

    @classmethod
    def format(cls, records):
        return [cls(*record) for record in records]
