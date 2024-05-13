# -*- coding: utf-8 -*-

{
    'name': 'Asientos/Apuntes Contables',
    'version': '16.0.0.0',
    'license': 'AGPL-3',
    'author': 'Elitumdevelop',
    'depends': [
        'base', 'account', 'stock_account', 'stock',
    ],
    'data': [
        'views/account_move.xml',
    ],
    'installable': True,
    'auto_install': False,
}
