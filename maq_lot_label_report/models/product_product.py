# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    govt_sku = fields.Char("Govt. SKU")
