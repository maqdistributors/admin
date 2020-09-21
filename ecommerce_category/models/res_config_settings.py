# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    website_shop_login = fields.Boolean(related='website_id.website_shop_login')
    website_shop_login_redirect = fields.Char(related='website_id.website_shop_login_redirect')