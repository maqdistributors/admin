# -*- coding: utf-8 -*-

import time
from odoo import models, fields, api, _


class ShopifyVariantExport(models.TransientModel):
    _name = 'export.shopify.variant'
    _description = "Shopify Product Variant Export"

    @api.multi
    def export_shopify_product_variant(self):
        shopify_prod_obj = self.env['shopify.product.product']
        for rec in self:
            active_ids = rec._context.get('active_ids')
            shopify_prod_search = shopify_prod_obj.search(
                [('id', 'in', active_ids), ("shopify_product_id", "in", ['', False])])
            # Add counter b'coz we can send only 2 request per second
            count = 1
            for product in shopify_prod_search:
                product.export_shopify_variant()
                if (count % 2 == 0):
                    time.sleep(0.5)
                count += 1
