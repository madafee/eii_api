# -*- coding: utf-8 -*-

import datetime
from hashlib import md5
import time
from project.database import models
from project import APP
from project.common import datadictionary as dd
from itertools import groupby
import requests
import requests
import time
import hashlib
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import  base64

__author__ = "liuxu"


def get_token():
    url = APP.config['QCC_TOKEN_HOST']
    try:
        r = requests.get(url)
        if r.status_code == 200:
            token = r.json()['token']
            return token
    except Exception as inst:
        APP.log.exception(inst)


def get_companylist(keyword, page_no, page_size):
    ts = str(int(time.time()))
    sign_key = APP.config['QCC_KEY'] + ts + APP.config['QCC_SECRET']
    token_sign = md5(sign_key.encode(encoding='utf-8')).hexdigest().upper()

    url = (
        'https://pro.qcc.com/api/yj/ECIV4/SearchWide'
        '?key={key}&keyword={keyword}&pageSize={page_size}&pageIndex={page_no}'
        '&type=name'
        .format(
            key=APP.config['QCC_KEY'],
            keyword=keyword,
            page_size=page_size,
            page_no=page_no))

    headers = {
        'Connection': 'close',
        'Token': token_sign,
        'Timespan': ts,
    }

    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            body = r.json()
            if body.get('Status') == '200':
                return body
            else:
                APP.log.exception(str(r.json()))
    except Exception as inst:
        APP.log.exception(inst)


def get_company(keyword):
    ts = str(int(time.time()))
    sign_key = APP.config['QCC_KEY'] + ts + APP.config['QCC_SECRET']
    token_sign = md5(sign_key.encode(encoding='utf-8')).hexdigest().upper()

    url = (
        'https://pro.qcc.com/api/yj/ECIV4/GetBasicDetailsByName'
        '?key={key}&keyword={keyword}'
        .format(
            key=APP.config['QCC_KEY'],
            keyword=keyword))

    headers = {
        'Connection': 'close',
        'Token': token_sign,
        'Timespan': ts,
    }

    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            body = r.json()
            if body.get('Status') == '200':
                return body['Result']
            else:
                APP.log.exception(str(r.json()))
    except Exception as inst:
        APP.log.exception(inst)


def get_partners(company):
    ts = str(int(time.time()))
    sign_key = APP.config['QCC_KEY'] + ts + APP.config['QCC_SECRET']
    token_sign = md5(sign_key.encode(encoding='utf-8')).hexdigest().upper()

    url = (
        'https://pro.qcc.com/api/yj/ECIPartner/GetList'
        '?key={key}&searchKey={company}&pageSize=20'
        .format(
            key=APP.config['QCC_KEY'],
            company=company))

    headers = {
        'Connection': 'close',
        'Token': token_sign,
        'Timespan': ts,
    }

    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            body = r.json()
            if body.get('Status') == '200':
                ret = [{
                    'stockname': partner['StockName'],
                    'stocktype': partner['StockType'],
                    'stockpercent': partner['StockPercent'],
                    'shouldcapi': partner['ShouldCapi'],
                    'shouddate': partner['ShoudDate']}
                    for partner in body['Result']]
                return ret
            else:
                APP.log.exception(str(r.json()))
    except Exception as inst:
        APP.log.exception(inst)


def get_stocklist(company, percent=0):
    ts = str(int(time.time()))
    sign_key = APP.config['QCC_KEY'] + ts + APP.config['QCC_SECRET']
    token_sign = md5(sign_key.encode(encoding='utf-8')).hexdigest().upper()

    url = (
        'https://pro.qcc.com/api/bene/corps/stockList'
        '?key={key}&companyName={company}&percent={percent}&mode=2'
        .format(key=APP.config['QCC_KEY'], company=company, percent=percent))

    headers = {
        'Connection': 'close',
        'Token': token_sign,
        'Timespan': ts,
    }

    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            body = r.json()
            if body.get('status') == '200':
                stocklist = body['result']

                ret = {
                    'points': [{'name': company, 'percent': '100', 'records': []}],
                    'connects': []
                }

                for break_through in stocklist['breakThroughList']:
                    # 实体点名称及大小
                    ret['points'].append({
                        'name': break_through['name'],
                        'percent': break_through['totalStockPercent'][:-1],
                        'records': [
                            detail['path'] for detail in break_through['detailInfoList']]
                        })

                    # 实体点之间关系
                    for detail in break_through['detailInfoList']:
                        # 拆解路径(陈德强(90%)->苏州知彼信息科技中心(有限合伙)(12.3583%)->企查查科技有限公司)
                        paths = detail['path'].split('->')
                        for i in range(len(paths)-1):
                            # 起点
                            pos = paths[i].rfind('(')
                            if pos != -1:
                                source = paths[i][:pos]
                                value = paths[i][pos+1:-2]
                            else:
                                source = paths[i]
                                value = 0.0

                            # 终点
                            pos = paths[i+1].rfind('(')
                            if pos != -1:
                                dest = paths[i+1][:pos]
                            else:
                                dest = paths[i+1]

                            ret['connects'].append({
                                'source': source,
                                'dest': dest,
                                'value': value})
                return ret
            else:
                APP.log.exception(str(r.json()))
    except Exception as inst:
        APP.log.exception(inst)

