# -*- coding: utf-8 -*-

from jsonschema import validate


class Json(object):
    @staticmethod
    def check(value, schema):
        validate(value, schema)
        return value

    '''
    valid:
        1. {'staff_id':员工ID, 'req': 顺序}
    '''
    STAFF_REQ = {
        "type": "object",
        "required": [
            "staff_id",
            "req"
        ],
        "properties": {
            "staff_id": {
                "type": "number"
            },
            "req": {
                "type": "number"
            }
        }
    }

    '''
    valid:
        1. {
            'staff_id':员工ID,
            'department_id': 科室ID,
            attendance:[{'date': '日期', 'type_id': 类型ID}]}
    '''
    SCHEDULES = {
        "type": "object",
        "required": [
            "staff_id",
            "department_id",
            "schedule_data"
        ],
        "properties": {
            "staff_id": {
                "type": "number"
            },
            "department_id": {
                "type": "number"
            },
            "schedule_data": {
                "type": "array",
                "items": [
                    {
                        "type": "object",
                        "required": [
                            "date",
                            "type_id"
                        ],
                        "properties": {
                            "mode": {
                                "date": "string"
                            },
                            "duration": {
                                "type_id": "number"
                            }
                        }
                    }
                ]
            }
        }
    }


