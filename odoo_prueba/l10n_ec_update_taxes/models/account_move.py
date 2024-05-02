# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta

from odoo.tools import format_date, frozendict


class AccountRecompute(models.Model):
    _inherit = 'account.move'

    def recompute_iva_subtotal(self):
        self.ensure_one()

        account_line = self.env['account.move.line'].search([('move_id', '=', self.id)])
        #self.env.add_to_compute(model._fields['tax_ids'], model.search([]))

        for line in account_line:
            line.tax_ids = line._get_computed_taxes()
            #line.tax_ids = line._compute_all_tax()
            print(line.tax_ids)
            print(line.compute_all_tax)

        print(self.env['account.move.line'].search([('move_id', '=', self.id)]).mapped('compute_all_tax'))



# account_line = self.env['account.move.line'].search([('move_id', '=',
# self.id)]).mapped('product_id')
# account_line.recompute()
# for product in account_line.product_id:
# account_line.product_id.write({'id': product})
# print(product.taxes_id.name)

# print(account_line)
# TENGO EXPERIENCIA EN EL AREA DE LABORATORIO DE COMPUTACION.
#Me gustaria ayudar a la comunidad politecnica con mis conocimientos.