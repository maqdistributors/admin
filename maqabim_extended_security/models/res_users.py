# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    pos_ids = fields.Many2many('pos.config', 'res_users_pos_configuration_rel', 'user_id', 'pos_id', string='Allowed Pos')
    warehouse_ids = fields.Many2many('stock.warehouse', 'res_user_warehouse_rel', 'user_id', 'warehouse_id', string='Allowed Warehouses', domain="[('company_id', '=', company_id)]")

    @api.onchange('pos_ids', 'warehouse_ids')
    def rewrite_company(self):
    	# WIERD HACK: JUST KILL
    	self.env.user.write({'company_id': self.env.user.company_id.id})
