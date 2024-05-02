# -*- coding: utf-8 -*-

{
    'name': 'Ticket-Tarea',
    'version': '16.0.0.0',
    'license': 'AGPL-3',
    'author': 'Elitumdevelop',
    'depends': [
        'base', 'helpdesk', 'project', 'helpdesk_timesheet'
    ],
    'data': [
        'wizard/create_task_wizard_view.xml',
        'security/ir.model.access.csv',
        'views/team_coordinator_view.xml',
        'views/create_ticket_to_task_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
