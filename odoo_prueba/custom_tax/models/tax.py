# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta

from odoo.tools import format_date


class Tax(models.Model):
    _inherit = 'account.tax'

    @api.onchange('amount', 'tax_group_id', 'type_tax_use')
    def _onchange_check_taxes(self):
        if self.id.origin:
            account_move_tax = self.env['account.move.line'].search_count([('tax_ids', '=', self.id.origin)])
            if account_move_tax > 0:
                raise ValidationError(
                    "No puede modificar este impuesto debido a que esta siendo usado en un asiento contable.")