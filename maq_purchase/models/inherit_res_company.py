# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if self._context.get('allowed_companies_only'):
            company_ids = self.env['res.users'].browse(self._uid).company_ids
            if company_ids:
                return company_ids.name_get()
        return super(ResCompany, self).name_search(name, args, operator, limit)
