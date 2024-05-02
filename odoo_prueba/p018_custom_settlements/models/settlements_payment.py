# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta

from odoo.tools import format_date


class NewPayment(models.Model):
    _inherit = 'account.payment'

    @api.onchange('movement_reference')
    def _onchange_movement_reference(self):
        payment = self.env['account.payment'].browse(self._context['active_id'])
        print(payment)
        if self.cancellation_reason:
            settlements = self.env['hr.payslip.settlement'].search([('payment_ids', '=', self.id.origin)])
            print(settlements)
            print(self.state)
            print(self.env['hr.payslip.settlement'].search([('payment_ids', '=', self.id.origin)]).mapped('payment_state'))
            settlements.write({'payment_state': 'no credits'})
            print(self.env['hr.payslip.settlement'].search([('payment_ids', '=', self.id.origin)]).mapped('payment_state'))


class NewPaymentCancelWizard(models.TransientModel):
    _inherit = 'account.payment.cancel.wizard'

    def action_confirm_cancel(self):
        payment = self.env['account.payment'].browse(self._context['active_id'])

        settlements = self.env['hr.payslip.settlement'].search([('payment_ids', '=', payment.id)])
        settlements.write({'payment_state': 'no credits'})

        payment.move_id.with_context(allow_remove_move_reconcile=True, cancellation_reason=self.reason).button_cancel()
        return True
