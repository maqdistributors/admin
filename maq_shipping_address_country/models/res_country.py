# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCountry(models.Model):
    _inherit = 'res.country'

    def get_website_sale_countries(self, mode='billing'):
        res = super(ResCountry, self).get_website_sale_countries(mode=mode)
        if mode == 'shipping':
            current_website_id = self.env['website'].get_current_website()
            country_id = current_website_id.company_id.country_id
            if country_id in res:
                return res
            else:
                res |= country_id
        return res
