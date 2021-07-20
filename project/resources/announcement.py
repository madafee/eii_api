# -*- coding: utf-8 -*-

from project import APP
from project.common import resource
from project.common import response
from project.common import decorator
from project.common import datadictionary as dd
import requests

__author__ = 'liuxu'
# 公告管理


@APP.api.resource('/announcements')
class Announcements(resource.Resource):
    def __init__(self):
        super(Announcements, self).__init__()

    # 取得公告列表
    @decorator.query_params('keyword')  # 检索关键字，用户姓名
    @decorator.query_params('start_date')  # 开始时间
    @decorator.query_params('end_date')  # 结束时间
    @decorator.get_page
    def get(self, **kwargs):
        host = r'https://efts.sec.gov/LATEST/search-index'
        headers = {'User-Agent': 'Mozilla/5.0', 'Connection': 'close'}
        data = {
            'q': kwargs['keyword'],
            'startdt': kwargs['start_date'],
            'enddt': kwargs['end_date'],
            'page': kwargs['page'][0],
            'from': kwargs['page'][1]}

        r = requests.post(host, json=data, headers=headers, timeout=20)

        body = r.json()

        announcements = []

        total = body['hits']['total']['value']
        for hit in body['hits']['hits']:
            name = hit['_source']['form']
            name = dd.AnnouncementType.get(name) or name

            announcement = {
                'name': name,
                'filed_date': hit['_source']['file_date'],
                'report_date': hit['_source']['period_ending'],
                'source': hit['_source']['display_names'][0],
                'location': hit['_source']['biz_locations'][0],
                'file': ('https://www.sec.gov/Archives/edgar/data/{}/{}'
                         .format(hit['_source']['ciks'][0],
                                 hit['_id'].replace('-', '').replace(':', '/')))}
            announcements.append(announcement)

        return response.get_value(announcements, response.Fields.ANNOUNCEMENTS)

