# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, tools

from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression

from collections import defaultdict
from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta

from odoo.tools import format_date


class Stage(models.Model):
    _inherit = 'project.task.type'

    is_terminated = fields.Boolean(string='¿La tarea esta terminada?', default=False)


class TaskTerminated(models.Model):
    _inherit = 'project.task'

    is_terminated = fields.Boolean(string='Terminada', compute='_compute_task', default=False)

    def _compute_task(self):
        for task in self:
            if task.stage_id.is_terminated:
                task.is_terminated = True
            else:
                task.is_terminated = False

