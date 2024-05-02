# -*- coding: utf-8 -*-

{
    'name': 'Nomina-Reglas',
    'version': '16.0.0.0',
    'license': 'AGPL-3',
    'author': 'Elitumdevelop',
    'depends': [
        'base', 'custom_account', 'payment',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/payslip_report_security.xml',
        'views/payslip_rule.xml',
    ],
    'installable': True,
    'auto_install': False,
}
