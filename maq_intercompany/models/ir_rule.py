# -*- coding: utf-8 -*-
from odoo import models, fields, api


class IrRule(models.Model):

    _inherit = 'ir.rule'

    @api.model
    def company_erp_manager(self):
        '''Added the Company erp manager rule for company fields so that custom group user
           can access all the companies'''
        rule_id = self.env.ref("base.res_company_rule_erp_manager")
        if rule_id.groups:
            rule_id.write({'groups':[(3,rule_id.groups.id)]})
        if not rule_id.groups:
            rule_id.write({'groups':[(6, 0, [self.env.ref('maq_intercompany.maq_company_admin_manager').id])]})
