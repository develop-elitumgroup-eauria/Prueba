# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta

from odoo.tools import format_date


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    is_deducible = fields.Boolean(string='Es deducible?', default=False)
