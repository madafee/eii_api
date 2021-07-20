# -*- coding: utf-8 -*-

import gevent
from gevent import pool
import uuid
from collections import OrderedDict
import datetime
import xlsxwriter
from project.database import models
from project import APP
from project.common import qcc
from project.common import utils
from project.common import datadictionary as dd
from project.common import exception as ex

__author__ = "liuxu"


def update_company(company_id):
    company = models.TblCompany.query.filter_by(id=company_id).first()
    new_company = qcc.get_company(company.keyno)
    partners = qcc.get_partners(new_company['Name'])
    stocklist = qcc.get_stocklist(new_company['Name'])
    changes = []

    company.update(
        name=new_company['Name'],
        no=new_company['No'],
        belongorg=new_company['BelongOrg'],
        operid=new_company['OperId'],
        opername=new_company['OperName'],
        startdate=new_company['StartDate'],
        enddate=new_company['EndDate'],
        status=new_company['Status'],
        province=new_company['Province'],
        updateddate=new_company['UpdatedDate'],
        creditcode=new_company['CreditCode'],
        registcapi=new_company['RegistCapi'],
        econkind=new_company['EconKind'],
        address=new_company['Address'],
        scope=new_company['Scope'],
        termstart=new_company['TermStart'],
        teamend=new_company['TeamEnd'],
        checkdate=new_company['CheckDate'],
        orgno=new_company['OrgNo'],
        isonstock=new_company['IsOnStock'],
        stocknumber=new_company['StockNumber'],
        stocktype=new_company['StockType'],
        enttype=new_company['EntType'],
        reccap=new_company['RecCap'],
        partners=partners)

    source_points = {
        point['name']: point['percent']
        for point in company.stocklist['points']}
    dest_points = {
        point['name']: point['percent']
        for point in stocklist['points']}

    for name, percent in dest_points.items():
        source_percent = source_points.get(name)

        if not source_percent:
            changes.append('新进{}{}%'.format(name, percent))
        elif source_percent == percent:
            continue
        elif float(source_percent) > float(percent):
            changes.append('{}减持{}%'.format(
                name, round(float(source_percent) - float(percent))))
        elif float(source_percent) < float(percent):
            changes.append('{}增持{}%'.format(
                name, round(float(percent) - float(source_percent), 4)))

    for name, percent in source_points.items():
        if not dest_points.get(name):
            changes.append('退出{}{}%'.format(name, percent))

    if changes:
        models.TblStockChange.create(
            company_id=company.id,
            old_stocklist=company.stocklist,
            new_stocklist=stocklist,
            change_info=changes)
        company.update(stocklist=stocklist, stock_datetime=datetime.datetime.now())

    models.DB.session.commit()


def insert_company(company_id):
    company = models.TblCompany.query.filter_by(id=company_id).first()

    companys = qcc.get_companylist(company.name, 1, 10)
    for com in companys['Result']:
        if com['Name'] == company.name:
            keyno = com['KeyNo']
            break
    else:
        models.DB.session.commit()
        return

    new_company = qcc.get_company(keyno)
    partners = qcc.get_partners(new_company['Name'])
    stocklist = qcc.get_stocklist(new_company['Name'])

    company.update(
        keyno=new_company['KeyNo'],
        name=new_company['Name'],
        no=new_company['No'],
        belongorg=new_company['BelongOrg'],
        operid=new_company['OperId'],
        opername=new_company['OperName'],
        startdate=new_company['StartDate'],
        enddate=new_company['EndDate'],
        status=new_company['Status'],
        province=new_company['Province'],
        updateddate=new_company['UpdatedDate'],
        creditcode=new_company['CreditCode'],
        registcapi=new_company['RegistCapi'],
        econkind=new_company['EconKind'],
        address=new_company['Address'],
        scope=new_company['Scope'],
        termstart=new_company['TermStart'],
        teamend=new_company['TeamEnd'],
        checkdate=new_company['CheckDate'],
        orgno=new_company['OrgNo'],
        isonstock=new_company['IsOnStock'],
        stocknumber=new_company['StockNumber'],
        stocktype=new_company['StockType'],
        stocklist=stocklist,
        stock_datetime=datetime.datetime.now(),
        enttype=new_company['EntType'],
        reccap=new_company['RecCap'],
        partners=partners)

    models.DB.session.commit()


@APP.scheduler.task('cron', id='track_stock', hour='20', minute='55')
def track_stock():
    APP.log.info('scheduler: track_stock start')
    companys = models.TblCompany.query.filter_by(is_track=1).all()

    pools = pool.Pool(20)
    jobs = [
        pools.spawn(update_company, company.id)
        for company in companys]
    gevent.joinall(jobs, timeout=7200)

    APP.log.info('scheduler: track_stock end')


@APP.scheduler.task('cron', id='import_company', hour='00', minute='14')
def import_company():
    APP.log.info('scheduler: import_company start')
    companys = models.TblCompany.query.filter(models.TblCompany.keyno.is_(None)).all()

    pools = pool.Pool(20)
    jobs = [
        pools.spawn(insert_company, company.id)
        for company in companys]
    models.DB.session.commit()
    gevent.joinall(jobs, timeout=7200)

    APP.log.info('scheduler: import_company end')


# 股权Excel
def generate_stocklist_xlsx(company):
    filename = '{}.xlsx'.format(uuid.uuid1())
    path = '/opt/temp/{}'.format(filename)

    # 清理临时文件夹
    utils.del_files('/opt/temp/')

    workbook = xlsxwriter.Workbook(path)
    worksheet = workbook.add_worksheet('股权穿透列表')

    # 标题栏
    header_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#87CEFA'})
    data1_format = workbook.add_format({
        'bold': 1,
        'valign': 'vcenter',
        'border': 1})
    data2_format = workbook.add_format({
        'bold': 1,
        'valign': 'vcenter',
        'border': 1,
        'fg_color': '#D3D3D3'})
    worksheet.set_column('A:A', 60)
    worksheet.set_column('B:B', 10)
    worksheet.set_column('C:C', 170)

    worksheet.write('A1', '公司名称', header_format)
    worksheet.write('B1', '控股比例', header_format)
    worksheet.write('C1', '穿透路径', header_format)

    stocklist = qcc.get_stocklist(company)

    line = 2
    for i, point in enumerate(stocklist['points']):
        start = line

        if not point['records']:
            worksheet.write(
                'C{}'.format(line), '', data1_format if i % 2 else data2_format)
            line += 1
        else:
            for record in point['records']:
                worksheet.write(
                    'C{}'.format(line), record, data1_format if i % 2 else data2_format)
                line += 1

        if start == line - 1:
            worksheet.write(
                'A{}'.format(start),
                point['name'],
                data1_format if i % 2 else data2_format
                )
            worksheet.write(
                'B{}'.format(start),
                '{}%'.format(point['percent']),
                data1_format if i % 2 else data2_format
                )
        else:
            worksheet.merge_range(
                'A{}:A{}'.format(start, line - 1),
                point['name'],
                data1_format if i % 2 else data2_format)
            worksheet.merge_range(
                'B{}:B{}'.format(start, line - 1),
                '{}%'.format(point['percent']),
                data1_format if i % 2 else data2_format)
    workbook.close()

    return path, filename


# 股权变更Excel
def generate_stockchange_xlsx(changes):
    filename = '{}.xlsx'.format(uuid.uuid1())
    path = '/opt/temp/{}'.format(filename)

    # 清理临时文件夹
    utils.del_files('/opt/temp/')

    workbook = xlsxwriter.Workbook(path)
    worksheet = workbook.add_worksheet('股权变更列表')

    # 标题栏
    header_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter',
        'fg_color': '#87CEFA'})
    data1_format = workbook.add_format({
        'bold': 1,
        'valign': 'vcenter',
        'border': 1})
    data2_format = workbook.add_format({
        'bold': 1,
        'valign': 'vcenter',
        'border': 1,
        'fg_color': '#D3D3D3'})
    worksheet.set_column('A:A', 60)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 170)

    worksheet.write('A1', '公司名称', header_format)
    worksheet.write('B1', '变更日期', header_format)
    worksheet.write('C1', '变更信息', header_format)

    for i, change in enumerate(changes):
        line = [
            change.company.name,
            str(change.create_datetime),
            ','.join(change.change_info),
        ]
        worksheet.write_row(
            'A{}'.format(i+2),
            line,
            data1_format if i % 2 else data2_format)

    workbook.close()

    return path, filename
