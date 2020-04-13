# -*- coding: utf-8 -*-

import time
from odoo import models, fields, api, _


class ShopifyImportOrders(models.TransientModel):
    _name = 'shopify.import.orders'
    _description = "Shopify Import Orders"

    shopify_order_id = fields.Char(string='Shopify Order id', 
        help='Shopify Order Id', track_visibility='onchange', required=True)

    @api.multi
    def import_shopify_orders(self):
        shopify_config_obj = self.env['shopify.config']
        for rec in self:
            shopify_order_id = rec.shopify_order_id
            active_ids = rec._context.get('active_ids')
            if active_ids:
                shopify_config_rec = shopify_config_obj.search([('id', 'in', active_ids)])
                shopify_config_rec.test_import_orders(shopify_order_id)
