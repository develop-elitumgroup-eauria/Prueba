# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools


class AccountMove(models.Model):
    _inherit = 'account.move'  # Asiento
    # compute = '_compute_stock_picking'

    stock_picking_id = fields.Many2one(
        'stock.picking', string='Picking asociado', compute='_compute_stock_picking',
        domain="[('journal_id.code', 'ilike', 'STJ')]")

    stock_move_line_id = fields.Many2one('stock.move.line', string='Movimiento de producto',
                                         compute='_compute_stock_move_line')
    stock_move_type = fields.Selection([('entry', 'Entrada'),
                                        ('out', 'Salida')], string='Tipo de movimiento')

    @api.depends('journal_id', 'stock_move_id')
    def _compute_stock_picking(self):
        if self.journal_id.code == 'STJ':
            stock_move = self.env['stock.move'].search([('account_move_ids', '=', self.id)])
            for record in stock_move:
                self.stock_picking_id = record.picking_id
        else:
            self.stock_picking_id = ''

    def _compute_stock_move_line(self):
        if self.journal_id.code == 'STJ':
            stock_move_line = self.env['stock.move'].search([('account_move_ids', '=', self.id)])
            for record in stock_move_line:
                self.stock_move_line_id = record.move_line_ids
        else:
            self.stock_move_line_id = ''


class StockMove(models.Model):
    _inherit = 'stock.move'  # Movimiento de existencia

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, svl_id, description):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        self.ensure_one()

        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating the accounting entries.
        debit_value = self.company_id.currency_id.round(cost)
        credit_value = debit_value

        valuation_partner_id = self._get_partner_id_for_valuation_lines()

        ##
        # account_move = self.env['account.move'].search([('stock_move_id', '=', self.id)])
        # for record in account_move:
        #     record.stock_picking_id = self.picking_id

        ##
        res = [(0, 0, line_vals) for line_vals in
               self._generate_valuation_lines_data(valuation_partner_id, qty, debit_value, credit_value,
                                                   debit_account_id, credit_account_id, svl_id, description).values()]

        return res
