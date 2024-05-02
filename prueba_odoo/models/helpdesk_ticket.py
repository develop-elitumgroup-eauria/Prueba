# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta

from odoo.tools import format_date


class Coordinator(models.Model):
    _inherit = 'helpdesk.team'

    coordinator_id = fields.Many2one('res.users', string='Coordinador')


class ProjectTicket(models.Model):
    _inherit = 'project.task'

    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket')
    is_terminated = fields.Boolean(string='Terminada', compute='_compute_task', default=False)

    def _compute_task(self):
        for task in self:
            if task.stage_id.is_terminated:
                task.is_terminated = True
            else:
                task.is_terminated = False


class Task(models.TransientModel):
    _name = 'helpdesk.task'
    _description = 'Create a task'

    name = fields.Char('Titulo', required=True)
    description = fields.Html('Descripcion')
    project_id = fields.Many2one('project.project', string='Proyecto', required=True)
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', required=True)
    user_ids = fields.Many2many('res.users', string='Asignados', required=True)

    def _generate_task_values(self):
        self.ensure_one()

        return {
            'name': self.name,
            'description': self.description,
            'project_id': self.project_id.id,
            'ticket_id': self.ticket_id.id,
            'user_ids': [(6, 0, self.user_ids.ids)]
        }

    def action_generate_task(self):
        self.ensure_one()

        new_task = self.env['project.task'].create(self._generate_task_values())
        return new_task

    def action_generate_and_view_task(self):
        self.ensure_one()
        new_task = self.action_generate_task()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tasks from Tickets'),
            'res_model': 'project.task',
            'res_id': new_task.id,
            'view_mode': 'form',
            'view_id': self.env.ref('project.view_task_form2').id,
            'context': {
                'fsm_mode': True,
                'create': False,
            }
        }


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    tasks_id = fields.One2many('project.task', 'ticket_id', string='Tasks')
    task_count = fields.Integer(compute='_compute_task_count')

    def _compute_task_count(self):
        for ticket in self:
            ticket.task_count = self.env['project.task'].search_count(
                [('ticket_id', '=', self.id)])

    def action_view_task(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks',
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'domain': [('ticket_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def create_task(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _("Crear Tarea"),
            'res_model': 'helpdesk.task',
            'context': {"default_ticket_id": self.id,
                        "default_user_ids": [(4, self.team_id.coordinator_id.id)],
                        "default_name": self.name,
                        "default_project_id": self.team_id.project_id.id,
                        "default_description": self.description
                        },
            'view_mode': 'form',
            'view_id': self.env.ref('prueba_odoo.create_task_view_form').id,
            'target': 'new'
        }




class Stage(models.Model):
    _inherit = 'project.task.type'

    is_terminated = fields.Boolean(string='¿La tarea esta terminada?', default=False)


class Tax(models.Model):
    _inherit = 'account.tax'

    @api.onchange('amount', 'tax_group_id')
    def _onchange_check_taxes(self):
        if self.id.origin:
            account_move_tax = self.env['account.move.line'].search_count([('tax_ids', '=', self.id.origin)])
            if account_move_tax > 0:
                raise ValidationError(
                    "No puede modificar este impuesto debido a que esta siendo usado en un asiento contable.")





class Code(models.Model):
    _inherit = 'hr.salary.rule'

    code_name = fields.Char('Code Name', compute='_compute_code', store=True)

    def _compute_code(self):
        for rule in self:
            rule.code_name = rule.name


class Nomina(models.Model):
    _name = 'nomina.report.prueba'
    _description = 'Nomina Report'
    _auto = False
    _rec_name = 'date_from'
    _order = 'date_from desc'

    salary_rules_id = fields.Many2one('hr.salary.rule', 'Salary Rules', readonly=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', readonly=True)
    department_id = fields.Many2one('hr.department', 'Department', readonly=True)
    date_from = fields.Date('Start Date', readonly=True)
    date_to = fields.Date('End Date', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)

    # count_payslip = fields.Integer('# Payslip', group_operator="avg", readonly=True)
    total_rule = fields.Float('Total', readonly=True)
    net_wage = fields.Float('Net Wage', readonly=True)
    count_payslip = fields.Integer('# Payslip', readonly=True)

    code = fields.Char('Code')

    def _query(self):
        select_ = """        
               p.id as id,
               sr.id as salary_rules_id,
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


