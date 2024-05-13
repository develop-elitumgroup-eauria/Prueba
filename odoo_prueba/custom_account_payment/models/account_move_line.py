# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta

from odoo.tools import format_date


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    #is_deducible = fields.Boolean(string='Es deducible?', default=False)

    is_deducible = fields.Boolean(string='Es deducible?', default=False, compute='_compute_is_deducible')

    @api.depends('move_id.is_deducible')
    def _compute_is_deducible(self):
        for record in self:
            if record.move_id.is_deducible:
                record.is_deducible = True
            else:
                record.is_deducible = False
