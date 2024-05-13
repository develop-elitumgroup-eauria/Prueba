# -*- coding: utf-8 -*-

{
    'name': 'Apuntes Contables-Check',
    'version': '16.0.0.0',
    'license': 'AGPL-3',
    'author': 'Elitumdevelop',
    'depends': [
        'base', 'account', 'payment_checks',
    ],
    'data': [
        'views/account_move_view.xml',
        'views/account_move_line_view.xml',
        'views/account_payment_view.xml',
        'views/account_bank_note_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
