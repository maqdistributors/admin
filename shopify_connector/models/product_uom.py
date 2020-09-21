# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductUOM(models.Model):
    _inherit = 'uom.uom'

    is_shopify_uom = fields.Boolean(
        "Shopify UOM", default=True, help="To determine which product unit of measures to use on Shopify UOM field on product template")
