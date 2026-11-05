# -*- coding: utf-8 -*-
from odoo import models, fields


class CrmStage(models.Model):
    _inherit = 'crm.stage'

    need_cqs_passed = fields.Boolean(
        string="Need CQS Passed",
        default=False,
        help="If checked, opportunities currently in this stage must pass client qualification screening (FRM-SAL-01) "
             "or be overridden by a CQS Admin before they can be moved out to another stage."
    )
