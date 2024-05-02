# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta

from odoo.tools import format_date


class Code(models.Model):
    _inherit = 'hr.salary.rule'

    code_name = fields.Char('Code Name', compute='_compute_code', store=True)

    def _compute_code(self):
        for rule in self:
            rule.code_name = rule.name


class PayslipRules(models.Model):
    _name = 'payslip.rule'
    _description = 'Payslip Rule'
    _auto = False
    _rec_name = 'date_from'
    _order = 'date_from desc'

    # salary_rules_id = fields.Many2one('hr.salary.rule', 'Salary Rules', readonly=True, invisible=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', readonly=True)
    department_id = fields.Many2one('hr.department', 'Department', readonly=True)
    date_from = fields.Date('Start Date', readonly=True)
    date_to = fields.Date('End Date', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)

    total_rule = fields.Float('Total', readonly=True)
    net_wage = fields.Float('Net Wage', readonly=True, invisible=True)
    count_payslip = fields.Integer('# Payslip', readonly=True, invisible=True)

    code = fields.Char('Salary Rules')

    def _query(self):
        select_ = """        
               p.id as id,
               e.id as employee_id,
               d.id as department_id,
               p.date_from as date_from,
               p.date_to as date_to,
               e.company_id as company_id,
               sr.code_name as code,
               p.net_wage as net_wage,
               COUNT(DISTINCT pl.salary_rule_id) as count_payslip,
               pl.total as total_rule
           """

        from_ = """
               hr_payslip as p
               left join hr_payslip_line pl on (pl.slip_id = p.id)
               left join hr_employee e on (p.employee_id = e.id)
               left join hr_department d on (e.department_id = d.id)
               left join hr_salary_rule sr on (pl.salary_rule_id = sr.id) 
               WHERE p.state IN ('done', 'paid') 
           """

        groupby_ = """   
               e.company_id,         
               p.id, 
               pl.total,
               sr.id,
               d.id,
               e.id,
               p.date_from,
               p.date_to
           """

        return f'SELECT {select_} FROM {from_} GROUP BY {groupby_}'

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))


class NominaEmployee(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def compute_sheet(self):
        self.ensure_one()

        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            today = fields.date.today()
            first_day = today + relativedelta(day=1)
            last_day = today + relativedelta(day=31)
            if from_date == first_day and end_date == last_day:
                batch_name = from_date.strftime('%B %Y')
            else:
                batch_name = _('From %s to %s', format_date(self.env, from_date), format_date(self.env, end_date))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': batch_name,
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        # Develop from v14
        employees = self.employee_ids
        if not employees:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        # Prevent a payslip_run from having multiple payslips for the same employee
        employees -= payslip_run.slip_ids.employee_id
        success_result = {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }
        if not employees:
            return success_result

        Payslip = self.env['hr.payslip']

        contracts = employees._get_contracts(
            payslip_run.date_start, payslip_run.date_end, states=['open', 'close', 'cancel']
        ).filtered(lambda c: c.active)

        date_start = datetime.combine(fields.Datetime.to_datetime(payslip_run.date_start), datetime.min.time())
        date_stop = datetime.combine(fields.Datetime.to_datetime(payslip_run.date_end), datetime.max.time())

        contracts._generate_work_entries(date_start, date_stop)
        work_entries = self.env['hr.work.entry'].search([
            ('date_start', '<=', payslip_run.date_end),
            ('date_stop', '>=', payslip_run.date_start),
            ('employee_id', 'in', employees.ids),
        ])
        self._check_undefined_slots(work_entries, payslip_run)

        if self.structure_id.type_id.default_struct_id == self.structure_id:
            work_entries = work_entries.filtered(lambda work_entry: work_entry.state != 'validated')
            time_intervals_str = ''
            if work_entries._check_if_error():
                work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])

                for work_entry in work_entries.filtered(lambda w: w.state == 'conflict'):
                    work_entries_by_contract[work_entry.contract_id] |= work_entry

                for contract, work_entries in work_entries_by_contract.items():
                    conflicts = work_entries._to_intervals()
                    time_intervals_str = "\n - ".join(['', *["%s -> %s" % (s[0], s[1]) for s in conflicts._items]])
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Some work entries could not be validated.'),
                        'message': _('Time intervals to look for:%s', time_intervals_str),
                        'sticky': False,
                    }
                }

        default_values = Payslip.default_get(Payslip.fields_get())
        payslips_vals = []
        for contract in self._filter_contracts(contracts):
            values = dict(default_values, **{
                'name': _('New Payslip'),
                'employee_id': contract.employee_id.id,
                'payslip_run_id': payslip_run.id,
                'date_from': payslip_run.date_start,
                'date_to': payslip_run.date_end,
                'contract_id': contract.id,
                'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
            })
            payslips_vals.append(values)
        payslips = Payslip.with_context(tracking_disable=True).create(payslips_vals)
        payslips._compute_name()
        payslips.compute_sheet()
        payslip_run.state = 'verify'

        return success_result


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
