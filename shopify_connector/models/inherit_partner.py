# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_shopify = fields.Boolean(
        string="Is Shopify", help="Consider this record while importing SO from Shopify", track_visibility='onchange')
