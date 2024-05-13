# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta

from odoo.tools import format_date


class AccountBankNote(models.Model):
    _inherit = 'account.bank.note'

    is_deducible = fields.Boolean(string='Es deducible?', default=False)

    @api.onchange('is_deducible')
    def _onchange_is_deducible(self):
        account_move = self.env['account.move'].search([('bank_note_id', '=', self.id.origin)])
        for move in account_move:
            move.is_deducible = self.is_deducible



