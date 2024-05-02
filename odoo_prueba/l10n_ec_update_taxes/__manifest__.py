# -*- coding: utf-8 -*-

{
    'name': 'Contabilidad Ecuatoriana',
    'version': '16.0.0.0',
    'license': 'AGPL-3',
    'author': 'Elitumdevelop',
    'depends': [
        'base', 'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/tax_wizard_security.xml',
        'wizard/update_tax_wizard_view.xml',
        'views/tax_view.xml',
        'views/account_move_view.xml',

    ],
    'installable': True,
    'auto_install': False,
}
