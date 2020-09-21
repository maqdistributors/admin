# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        # website does not have any record rule so when user load website >setting 
        # it pull fiest website and related fields i.e. website_user_id and website_template_user_id 
        # and user may not access to such details as first website company may not be alloweded
        # incase of multi company, we will try to load websitre of his current company allowing
        # Website>setting to load and then user can chage to any allowded companies or users.
        user_company_websites = self.env['website'].search([('company_id', '=', self.env.user.company_id.id)])
        if user_company_websites:
            res.update({'website_id': user_company_websites.id})
        return res
