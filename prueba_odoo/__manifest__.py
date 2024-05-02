# -*- coding: utf-8 -*-

{
    'name': 'Prueba',
    'version': '16.0.0.0',
    'license': 'AGPL-3',
    'author': 'Elitumdevelop',
    'depends': [
        'helpdesk', 'base', 'project_helpdesk', 'timesheet_grid', 'project'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/nomina_report_security.xml',
        'views/prueba_odoo.xml',
        'views/prueba_example.xml',
    ],
    'installable': True,
    'auto_install': False,
}
