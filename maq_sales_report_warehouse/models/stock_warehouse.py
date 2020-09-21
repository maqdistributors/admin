# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockWarehouse(models.Model):

    _inherit = 'stock.warehouse'

    m_shopify_warehouse = fields.Boolean(string='Is Shopify Warehouse')