# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression



class Task(models.TransientModel):
    _name = 'helpdesk.task'
    _description = 'Create a task'

    name = fields.Char('Titulo', required=True)
    description = fields.Html('Descripcion')
    project_id = fields.Many2one('project.project', string='Proyecto', required=True)
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', required=True)
    user_ids = fields.Many2many('res.users', string='Asignados', required=True)

    def _generate_task_values(self):
        self.ensure_one()

        return {
            'name': self.name,
            'description': self.description,
            'project_id': self.project_id.id,
            'ticket_id': self.ticket_id.id,
            'user_ids': [(6, 0, self.user_ids.ids)]
        }

    def action_generate_task(self):
        self.ensure_one()

        new_task = self.env['project.task'].create(self._generate_task_values())
        return new_task

    def action_generate_and_view_task(self):
        self.ensure_one()
        new_task = self.action_generate_task()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tasks from Tickets'),
            'res_model': 'project.task',
            'res_id': new_task.id,
            'view_mode': 'form',
            'view_id': self.env.ref('project.view_task_form2').id,
            'context': {
                'fsm_mode': True,
                'create': False,
            }
        }



