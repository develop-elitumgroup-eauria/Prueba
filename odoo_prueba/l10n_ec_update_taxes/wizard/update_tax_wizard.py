# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError


class UpdateTaxWizard(models.TransientModel):
    _name = 'update.tax.wizard'
    _description = _('Asistente para reemplazar impuestos')

    tax_old_id = fields.Many2one('account.tax', 'Impuesto a reemplazar')
    tax_new_id = fields.Many2one('account.tax', string='Reemplazar por', required=True)
    save_tax_old = fields.Boolean(string='Archivar impuesto antiguo', default=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)

    def save_tax(self):
        for record in self:
            tax_record = self.env['account.tax'].browse(self._context['active_id'])
            tax_record.tax_update_id = record.tax_new_id.id
            tax_record.is_updated = True
            #print(tax_record.tax_update_id)

            fiscal_position_tax = self.env['account.fiscal.position.tax'].search([('tax_dest_id', '=',
                                                                                   record.tax_old_id.id)])
            if fiscal_position_tax:
                fiscal_position_tax.write({'tax_dest_id': record.tax_new_id})
            else:
                fiscal_position_tax = self.env['account.fiscal.position.tax'].search([('tax_src_id', '=',
                                                                                       record.tax_old_id.id)])
                fiscal_position_tax.write({'tax_src_id': record.tax_new_id})

            if record.tax_old_id.type_tax_use == 'purchase':
                product_tax = self.env['product.template'].search([('supplier_taxes_id', '=', record.tax_old_id.id)])
                product_tax.write({'supplier_taxes_id': record.tax_new_id})

                company_tax = self.env['res.company'].search([('account_purchase_tax_id', '=', record.tax_old_id.id)])
                company_tax.write({'account_purchase_tax_id': record.tax_new_id})

            elif record.tax_old_id.type_tax_use == 'sale':
                product_tax = self.env['product.template'].search([('taxes_id', '=', record.tax_old_id.id)])
                product_tax.write({'taxes_id': record.tax_new_id})

                company_tax = self.env['res.company'].search([('account_sale_tax_id', '=', record.tax_old_id.id)])
                company_tax.write({'account_sale_tax_id': record.tax_new_id})

            record.tax_old_id.active = False
















 # account_move_tax = self.env['account.move.line'].search([('tax_ids', '=', record.tax_id.id)])