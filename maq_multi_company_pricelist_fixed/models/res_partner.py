# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api
from odoo.http import request


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.depends('country_id')
    def _compute_product_pricelist(self):
        # NOT A REAL PROPERTY !!!!
        # pricelist read as a admin user from the website
        # Fix Me if you have best solution
        user = request.env.user or self.env.user
        res = self.env['product.pricelist'].sudo(user=user)._get_partner_pricelist_multi(self.ids)
        for p in self:
            p.property_product_pricelist = res.get(p.id)
