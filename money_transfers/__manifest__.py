# -*- coding: utf-8 -*-
{
    'name': "Money Transfers",
    'summary': "Addons money transfers",
    'category': 'Uncategorized',
    'version': '1.0',
    'depends': ['base', 'mail', 'account', 'account_accountant'],
    'data': [
    'security/trans_security.xml',
    'security/ir.model.access.csv',
    'views/view.xml', 
    'report/transfer_copy_report.xml',
    'report/reportpaymentreceipt_report.xml',
    'report/receive_copy_report.xml',
    'report/reportpayment_receive_report.xml',
    'views/template.xml',
    'views/setting.xml',
    'views/recive.xml'
       ],
    'application': True,
    'installable': True,
    'images': ['static/description/icon.png'],

}