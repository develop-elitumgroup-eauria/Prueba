# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


class CoordinatorProject(models.Model):
    _inherit = 'helpdesk.team'

    coordinator_id = fields.Many2one('res.users', string='Coordinador')



