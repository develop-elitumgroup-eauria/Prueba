# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta

from odoo.tools import format_date


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_deducible = fields.Boolean(string='Es deducible?', default=False)

    @api.onchange('is_deducible')
    def _onchange_is_deducible(self):
        self.line_ids.is_deducible = self.is_deducible
        if self.bank_note_id:
            self.bank_note_id.is_deducible = self.is_deducible
