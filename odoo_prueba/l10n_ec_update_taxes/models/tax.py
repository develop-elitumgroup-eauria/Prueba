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

    tax_update_id = fields.Many2one('account.tax', string='Reemplazado por')
    is_updated = fields.Boolean(string='Hubo un reemplazo?', default=False)
    print(tax_update_id)

    def update_tax(self):
        self.ensure_one()
        print(self.tax_update_id)
        return {
            'type': 'ir.actions.act_window',
            'name': _("Asistente para reemplazar impuestos"),
            'res_model': 'update.tax.wizard',
            'context': {"default_tax_old_id": self.id,
                        "default_company_id": self.company_id.id,
                        },
            'view_mode': 'form',
            'view_id': self.env.ref('l10n_ec_update_taxes.update_tax_wizard_form').id,
            'target': 'new'
        }


