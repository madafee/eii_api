# -*- coding: utf-8 -*-

from sqlalchemy import func
import flask
from project import APP
from project.common import resource
from project.common import request
from project.common import response
from project.common import decorator
from project.common import common
from project.common import qcc
from project.common import utils
from project.common import datadictionary as dd
from project.common import exception as ex
from project.database.models import TblOrder
from project.database.models import TblOrderRecord
from project.database.models import TblUser
from project.database.models import TblCompany
from project.database.models import TblStockChange

__author__ = 'liuxu'
# 工单管理


@APP.api.resource('/companys')
class Companys(resource.Resource):
    req = request.RequestParser()
    # 公司key值
    req.add_body('keyword')
    # 是否追踪
    req.add_body('is_track')

    def __init__(self):
        super(Companys, self).__init__()

    # 取得公司列表
    @decorator.check_auth()
    @decorator.get_page
    @decorator.query_params('keyword')  # 检索关键字
    def get(self, **kwargs):
        keyword = kwargs['keyword']

        query = TblCompany.query
        if kwargs['keyword']:
            keyword = utils.get_fuzzy(kwargs['keyword'])
            query = (
                query
                .filter(
                    (TblCompany.name.like(keyword)) |
                    (TblCompany.no.like(keyword)) |
                    (TblCompany.creditcode.like(keyword))))

        companys = (
            query
            .order_by(TblCompany.update_datetime.desc())
            .paginate(*kwargs['page']))

        return response.get_value(companys, response.Fields.COMPANYS)

    # 新增公司信息
    @decorator.check_auth()
    def post(self, **kwargs):
        req_args = self.req.parse_args()

        count = TblCompany.query.count()
        if count >= int(APP.config['QCC_LIMIT']):
            raise ex.ReturnError('COMPANY_LIMIT')

        company = qcc.get_company(req_args['keyword'])
        stocklist = qcc.get_stocklist(company['Name'])
        partners = qcc.get_partners(company['Name'])

        if not TblCompany.query.filter_by(keyno=company['KeyNo']).first():
            TblCompany.create(
                keyno=company['KeyNo'],
                name=company['Name'],
                no=company['No'],
                belongorg=company['BelongOrg'],
                operid=company['OperId'],
                opername=company['OperName'],
                startdate=company['StartDate'],
                enddate=company['EndDate'],
                status=company['Status'],
                province=company['Province'],
                updateddate=company['UpdatedDate'],
                creditcode=company['CreditCode'],
                registcapi=company['RegistCapi'],
                econkind=company['EconKind'],
                address=company['Address'],
                scope=company['Scope'],
                termstart=company['TermStart'],
                teamend=company['TeamEnd'],
                checkdate=company['CheckDate'],
                orgno=company['OrgNo'],
                isonstock=company['IsOnStock'],
                stocknumber=company['StockNumber'],
                stocktype=company['StockType'],
                enttype=company['EntType'],
                reccap=company['RecCap'],
                stocklist=stocklist,
                partners=partners,
                is_track=req_args['is_track'])

        return response.get_code('OK')


@APP.api.resource('/companys/<int:id>')
class Company(resource.Resource):
    def __init__(self):
        super(Company, self).__init__()

    # 删除公司信息
    def delete(self, id, **kwargs):
        company = TblCompany.get(id)
        company.delete()

        return response.get_code('OK')

    # 取得公司信息详情
    def get(self, id, **kwargs):
        company = TblCompany.get(id)

        return response.get_value(company, response.Fields.COMPANY)


@APP.api.resource('/stockchanges')
class StockChanges(resource.Resource):
    def __init__(self):
        super(StockChanges, self).__init__()

    # 取得股权变更列表
    @decorator.check_auth()
    @decorator.get_page
    def get(self, **kwargs):
        stockchanges = (
            TblStockChange.query
            .order_by(TblStockChange.id.desc())
            .paginate(*kwargs['page']))

        return response.get_value(stockchanges, response.Fields.STOCKCHANGES)


@APP.api.resource('/companys/qcc')
class QCCCompanys(resource.Resource):
    def __init__(self):
        super(QCCCompanys, self).__init__()

    # 取得企查查公司列表
    @decorator.check_auth()
    @decorator.get_page
    @decorator.query_params('keyword')  # 检索关键字
    def get(self, **kwargs):
        keyword = kwargs['keyword']

        companys = qcc.get_companylist(keyword, kwargs['page'][0], kwargs['page'][1])
        ret = [{
            'keyno': company['KeyNo'],
            'name': company['Name'],
            'opername': company['OperName'],
            'startdate': company['StartDate'],
            'status': company['Status'],
            'no': company['No'],
            'creditcode': company['CreditCode']}
            for company in companys['Result']]

        count = companys['Paging']['TotalRecords']

        return response.get_value(ret, response.Fields.COMPANYS, count=count)


@APP.api.resource('/companys/qcc/<string:keyno>')
class QCCCompany(resource.Resource):
    def __init__(self):
        super(QCCCompany, self).__init__()

    # 取得企查查公司信息
    @decorator.check_auth()
    @decorator.query_params('percent')  # 穿透比例
    def get(self, keyno, **kwargs):
        percent = kwargs['percent'] or 0
        company = qcc.get_company(keyno)
        stocklist = qcc.get_stocklist(company['Name'], percent)
        partners = qcc.get_partners(company['Name'])

        company = TblCompany(
            keyno=company['KeyNo'],
            name=company['Name'],
            no=company['No'],
            belongorg=company['BelongOrg'],
            operid=company['OperId'],
            opername=company['OperName'],
            startdate=company['StartDate'],
            enddate=company['EndDate'],
            status=company['Status'],
            province=company['Province'],
            updateddate=company['UpdatedDate'],
            creditcode=company['CreditCode'],
            registcapi=company['RegistCapi'],
            econkind=company['EconKind'],
            address=company['Address'],
            scope=company['Scope'],
            termstart=company['TermStart'],
            teamend=company['TeamEnd'],
            checkdate=company['CheckDate'],
            orgno=company['OrgNo'],
            isonstock=company['IsOnStock'],
            stocknumber=company['StockNumber'],
            stocktype=company['StockType'],
            enttype=company['EntType'],
            reccap=company['RecCap'],
            stocklist=stocklist,
            partners=partners,
            is_track=1)

        return response.get_value(company, response.Fields.COMPANY)


@APP.api.resource('/companys/qcc/stock/export')
class QCCStockExcelExport(resource.Resource):
    def __init__(self):
        super(QCCStockExcelExport, self).__init__()

    # 导出股权穿透excel
    @decorator.query_params('company_name')  # 公司名称
    def get(self, **kwargs):
        company_name = kwargs['company_name']

        path, filename = common.generate_stocklist_xlsx(company_name)

        return flask.send_file(
            path,
            mimetype=('application/'
                      'vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            attachment_filename=filename,
            as_attachment=True)


@APP.api.resource('/companys/qcc/token')
class QCCCompanyToken(resource.Resource):
    def __init__(self):
        super(QCCCompanyToken, self).__init__()

    # 取得企查查公司token
    def get(self, **kwargs):

        token = qcc.get_token()
        ret = response.get_code('OK')
        ret['token'] = token
        return ret


@APP.api.resource('/companys/stock/change/export')
class StockChangeExcelExport(resource.Resource):
    def __init__(self):
        super(StockChangeExcelExport, self).__init__()

    # 导出股权变更excel
    @decorator.query_params('start_date')  # 开始时间(YYYY-MM-DD)
    @decorator.query_params('end_date')  # 结束时间(YYYY-MM-DD)
    def get(self, **kwargs):

        query = TblStockChange.query

        if kwargs['start_date']:
            start_date = request.Type.date(kwargs['start_date'])
            query = query.filter(TblStockChange.create_datetime >= start_date)

        if kwargs['end_date']:
            end_date = utils.add_days(request.Type.date(kwargs['end_date']))
            query = query.filter(TblStockChange.create_datetime < end_date)

        changes = query.all()

        path, filename = common.generate_stockchange_xlsx(changes)

        return flask.send_file(
            path,
            mimetype=('application/'
                      'vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            attachment_filename=filename,
            as_attachment=True)
